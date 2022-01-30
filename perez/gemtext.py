"""
perez.gemtext
=============
This implements the Gemtext parser and corresponding HTML generator.

:copyright: (C) 2022 Matthew Frazier
:license:   Revised BSD license, see LICENSE file for legal text
"""
import enum
import html
import re
from collections import namedtuple

class LineType(enum.Enum):
    TEXT = 'text'
    LINK = 'link'
    PRE_START = 'pre_start'
    PRE_END = 'pre_end'
    PRE = 'pre'
    QUOTED = 'quoted'
    LIST_ITEM = 'li'
    H1 = 'h1'
    H2 = 'h2'
    H3 = 'h3'


GEMTEXT_LINK_RE = re.compile(r'^=>\s*(\S+)\s+(.+)$')
GEMTEXT_OTHER_RE = re.compile(r'^(```|###|##|#|>|\* )\s*(.*)$')
GEMTEXT_OTHER_TYPES = {
    '```':  LineType.PRE_START,
    '* ':   LineType.LIST_ITEM,
    '#':    LineType.H1,
    '##':   LineType.H2,
    '###':  LineType.H3,
    '>':    LineType.QUOTED
}

Line = namedtuple('Line', ['type', 'first', 'last', 'text', 'extra', 'number'])


def iter_gemtext(gemtext):
    m2, m1, m0 = None, None, None
    pre_mode = False

    # TODO: should we allow the weird characters Python allows as newlines?
    for n, line in enumerate(gemtext.splitlines()):
        # This "for" loop yields each line on the iteration _after_ it is parsed.
        # m0 is where the line we parsed is stored.
        # m1 is where the 
        if pre_mode:
            if line.startswith('```'):
                m0 = (LineType.PRE_END, '', None)
                pre_mode = False
            else:
                m0 = (LineType.PRE, line, None)
        else:
            link_match = GEMTEXT_LINK_RE.match(line)
            if link_match:
                m0 = (LineType.LINK, link_match.group(2), link_match.group(1))
            else:
                other_match = GEMTEXT_OTHER_RE.match(line)
                if other_match:
                    lt = GEMTEXT_OTHER_TYPES[other_match.group(1)]
                    m0 = (lt, other_match.group(2), None)
                    if lt == LineType.PRE_START:
                        pre_mode = True
                else:
                    m0 = (LineType.TEXT, line, None)

        # This is where we emit m1.
        if m1 is not None:
            lt, text, extra = m1
            first = m2 is None or m2[0] != lt
            last = lt != m0[0]
            # n is the 0-based index of m0, which equals the 1-based index of m1.
            yield Line(lt, first, last, text, extra, n)

        # Advance the parser so the current m0 becomes m1 and will be emitted.
        m2, m1 = m1, m0

    # We need another copy of the code that emits m1 here.
    if m1 is not None:
        lt, text, extra = m1
        first = m2 is None or m2[0] != lt
        # This line will always be the last line of its type.
        # The last n is the 0-based index of m1, so we need to add 1.
        yield Line(lt, first, True, text, extra, n + 1)


def build_html(parsed_lines, proxy_hostname=None):
    for line in parsed_lines:
        lt = line.type
        escaped = html.escape(line.text)
        if lt == LineType.TEXT:
            yield '<p>' + escaped + '</p>'
        elif lt == LineType.LINK:
            href = line.extra
            open_tag = '<a href="' + html.escape(href, quote=True) + '">'
            yield open_tag + escaped + '</a>'
        elif lt == LineType.H1:
            yield '<h1>' + escaped + '</h1>'
        elif lt == LineType.H2:
            yield '<h2>' + escaped + '</h2>'
        elif lt == LineType.H3:
            yield '<h3>' + escaped + '</h3>'
        elif lt == LineType.LIST_ITEM:
            open_tag = '<ul><li>' if line.first else '<li>'
            close_tag = '</li></ul>' if line.last else '</li>'
            yield open_tag + escaped + close_tag
        elif lt == LineType.PRE:
            if line.first:
                if line.last:
                    yield '<pre>' + escaped + '</pre>'
                else:
                    yield '<pre>' + escaped
            elif line.last:
                yield escaped + '</pre>'
            else:
                yield escaped
        elif lt == LineType.PRE_START:
            if escaped:
                yield '<figure><figcaption>' + escaped + '</figcaption>'
            else:
                yield '<figure>'
        elif lt == LineType.PRE_END:
            yield '</figure>'
        elif lt == LineType.QUOTED:
            open_tag = '<blockquote><p>' if line.first else '<p>'
            close_tag = '</p></blockquote>' if line.last else '</p>'
            yield open_tag + escaped + close_tag
        else:
            raise NotImplementedError()


def gemtext_to_html(gemtext):
    return '\n'.join(build_html(iter_gemtext(gemtext)))
