import asyncio
import re
import ssl
import sys

STATUS_INPUT = 10
STATUS_SUCCESS = 20
STATUS_REDIRECT = 30
STATUS_TEMPFAIL = 40
STATUS_PERMFAIL = 50
STATUS_AUTH = 60

HEADER_LINE_SIZE = 1029
HEADER_RE = re.compile(r'^[1-6][0-9] .{1,1024}\r\n$')


# Until I upgrade this library to implement streaming,
# we are going to limit responses to 128 KiB.
TEMPORARY_RESPONSE_SIZE_LIMIT = 128 * 1024


def client_ssl_context(client_cert=None, require_ca=False):
    if client_cert is not None:
        raise NotImplementedError("Client cert support coming soon")

    # Most of this TLS code is borrowed from AV-98.
    # (C) 2019, 2020 Solderpunk <solderpunk@sdf.org>
    # https://tildegit.org/solderpunk/AV-98/src/branch/master/av98.py
    python3_version = sys.version_info.minor
    protocol = ssl.PROTOCOL_TLS if sys.version_info.minor >= 6 else ssl.PROTOCOL_TLSv1_2
    context = ssl.SSLContext(protocol)

    # TOFU mode only. TODO: Implement CA mode as an option.
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # Impose minimum TLS version.
    # In 3.7 and above, this is easy...
    if sys.version_info.minor >= 7:
        context.minimum_version = ssl.TLSVersion.TLSv1_2
    # Otherwise, it seems very hard...
    # The below is less strict than it ought to be, but trying to disable
    # TLS v1.1 here using ssl.OP_NO_TLSv1_1 produces unexpected failures
    # with recent versions of OpenSSL.  What a mess...
    else:
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_SSLv2
    # Try to enforce sensible ciphers.
    try:
        context.set_ciphers("AESGCM+ECDHE:AESGCM+DHE:CHACHA20+ECDHE:CHACHA20+DHE:!DSS:!SHA1:!MD5:@STRENGTH")
    except ssl.SSLError:
        # Rely on the server to only support sensible things, I guess...
        pass

    return context


class GeminiResponse(object):
    def __init__(self, gemini_url, status_code, header, body):
        self.gemini_url = gemini_url
        self.status_code = status_code
        self.status_type = status_code - status_code % 10
        self.header = header
        self.body = body


@asyncio.coroutine
async def gemini_request(host, path, *, port=1965, query=None, client_cert=None) -> GeminiResponse:
    # Validate URL.
    # TODO: Probably a lot more things to validate.
    # Servers will of course stop us from doing particularly stupid things,
    # but we should still be nice to them...
    if not isinstance(port, int) or port < 1 or port > 65535:
        raise TypeError("Invalid port number provided")
    port_string = '' if port == 1965 else f':{port}'
    gemini_url = 'gemini://' + host + port_string + path
    if query is not None:
        gemini_url = gemini_url + '?' + query
    url_encoded = gemini_url.encode('utf8') + b'\r\n'
    if len(url_encoded) > 1026:
        raise ValueError("Gemini URL is too long (1024-byte limit)")

    ssl = client_ssl_context(client_cert)
    reader, writer = await asyncio.open_connection(host, port, ssl=ssl)

    try:
        # TODO: We can validate the certificate at this point.
        # Transmit the URL...
        writer.write(url_encoded)
        await writer.drain()

        # Wait for a response...
        header_line_enc = await reader.readuntil(b'\n')
        if len(header_line_enc) > HEADER_LINE_SIZE:
            raise ValueError(f"Server sent a {len(header_line_enc)}-byte header line")
        header_line = header_line_enc.decode('utf8', errors='replace')
        m = HEADER_RE.match(header_line)
        if m is None:
            raise ValueError("Server sent an improperly formatted header line")

        status_code = int(header_line[:2])
        header = header_line[3:-2]

        if status_code >= 20 and status_code < 30:
            # We have a response body.
            body = await reader.read(TEMPORARY_RESPONSE_SIZE_LIMIT)
            while not reader.at_eof() and len(body) < TEMPORARY_RESPONSE_SIZE_LIMIT:
                size = TEMPORARY_RESPONSE_SIZE_LIMIT - len(body)
                body = body + await reader.read(size)
        else:
            body = None

        return GeminiResponse(gemini_url, status_code, header, body)
    finally:
        writer.close()
        await writer.wait_closed()
