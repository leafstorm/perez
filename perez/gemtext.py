import html
from os import link
import re

GEMTEXT_PRE = '```'
GEMTEXT_LINK_RE = re.compile(r'^=>\s*(\S+)\s+(.+)$')

def gemtext_to_html_lines(gemtext):
    output = []
    pre_lineno = None

    for line in gemtext.splitlines():
        if pre_lineno is None:
            # Handle lines _not_ in preformatted text mode.
            link_match = GEMTEXT_LINK_RE.match(line)
            if link_match:
                url = html.escape(link_match.group(1), quote=True)
                text = html.escape(link_match.group(2))
                output.append(f'<p><a href="{url}">{text}</a></p>')
            elif line.startswith('```'):
                # Enter preformatted text mode.
                # TODO: Handle alt text with figcaption
                output.append('')
                pre_lineno = 0
            else:
                output.append('<p>' + html.escape(line) + '</p>')
        else:
            # Handle lines in preformatted text mode.
            if line.startswith(GEMTEXT_PRE):
                if pre_lineno > 0:
                    output[-1] = output[-1] + '</pre>'
                output.append('')
                pre_lineno = None
            else:
                if pre_lineno == 0:
                    output.append('<pre>' + html.escape(line))
                else:
                    output.append(html.escape(line))
                pre_lineno += 1

    return '\n'.join(output)


def gemtext_to_html(gemtext):
    core = gemtext_to_html_lines(gemtext)
    return HTML_HEADER + core + HTML_FOOTER


HTML_HEADER = '''<!doctype html>
<html>
    <head>
        <title>Gemini</title>
    </head>
    <body>
        <main>
'''

HTML_FOOTER = '''
        </main>
    </body>
    <script src="/__static__/gemini_link_rewrite.js"></script>
</html>
'''
