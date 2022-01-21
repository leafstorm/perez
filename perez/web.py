"""
perez.web
=========
This implements the Gemini proxy as a Web application.

:copyright: (C) 2022 Matthew Frazier
:license:   Revised BSD license, see LICENSE file for legal text
"""
import os.path
import traceback
from aiohttp import web
from cgi import parse_header
from .gemini import gemini_request, STATUS_SUCCESS
from .gemtext import gemtext_to_html

HOST_RE = r'[a-z0-9-]+(?:\.[a-z0-9-]+)*'
PATH_RE = r'/.*'

NOSLASH_ROUTE = '/{host:' + HOST_RE + '}'
GEMINI_ROUTE = '/{host:' + HOST_RE + '}{path:' + PATH_RE + '}'

STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


async def index_handler(request: web.Request):
    return web.Response(text="Hello, world!")


async def noslash_handler(request: web.Request):
    host = request.match_info['host']
    reversed = request.app.router['gemini'].url_for(host=host, path='/')
    if 'q' in request.query:
        reversed = reversed.with_query({'q': request.query['q']})
    return web.HTTPFound(location=reversed)


async def gemini_handler(request: web.Request):
    host = request.match_info['host']
    path = request.match_info['path']
    if 'q' in request.query:
        query = request.query['q']
    else:
        query = None

    try:
        response = await gemini_request(host, path, query=query)
    except Exception as e:
        tb = traceback.format_exc()
        raise web.HTTPBadGateway(text=tb)

    if response.status_type == STATUS_SUCCESS:
        # Process the MIME type.
        mimetype, options = parse_header(response.header)
        if not mimetype.startswith('text/'):
            charset = None
        elif 'charset' in options:
            charset = options['charset']
        else:
            charset = 'UTF-8'

        if mimetype == 'text/gemini':
            # TODO: Convert gemtext to HTML.
            # For now, we're going to display it as text/plain.
            gemtext = response.body.decode(charset)
            html = gemtext_to_html(gemtext)
            body = html.encode('UTF-8')
            mimetype = 'text/html'
            charset = 'UTF-8'
        else:
            body = response.body
        return web.Response(body=body, content_type=mimetype, charset=charset)
    else:
        return web.Response(text=f'{response.status_code}: {response.header}')


def create_app():
    app = web.Application()
    app.add_routes([
        web.static('/__static__', STATIC_FOLDER),
        web.get('/', index_handler, name='index'),
        web.get(NOSLASH_ROUTE, noslash_handler, name='noslash'),
        web.get(GEMINI_ROUTE, gemini_handler, name='gemini'),
    ])
    return app


def main():
    app = create_app()
    web.run_app(app, host='127.0.0.1', port=8965)
