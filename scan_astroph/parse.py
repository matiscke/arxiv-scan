"""Functions relating to parsing Arxiv.org"""
import re

from .entry_evaluation import Entry

REGEX_TEMPLATE = \
r'''<dt><a name="item(?P<number>\d+)">.*<span class="list-identifier"><a href="/abs/(?P<id>[0-9.]*)".*</a> {ignore_pattern}.*</span></dt>
<dd>
<div class="meta">
<div class="list\-title mathjax">\s*
<span class="descriptor">Title:</span>\s*(?P<title>.*)
</div>
<div class="list\-authors">
<span class="descriptor">Authors:</span>\s*
(?P<authors>[\s\S]*?)
</div>'''
REGEX_AUTHORS = r'<a href=".*">(.*)</a>.*\n?'

def parse_html(html_data, cross_lists=True, resubmissions=False):
    """Scan content and retrieve entries

    We use regular expressions REGEX and REGEX_AUTHORS.
    The return value is a list containing Entry objects.
    """
    entries = []
    ignore_pattern = ""
    if not cross_lists:
        ignore_pattern += r'(?!\(cross-list)'
    if not resubmissions:
        ignore_pattern += r'(?!\(replaced)'

    regex = REGEX_TEMPLATE.format(ignore_pattern=ignore_pattern)
    for m in re.finditer(regex, html_data):
        authors = m.group("authors")
        author_list = re.findall(REGEX_AUTHORS, authors)
        entries.append(
            Entry(
                number=m.group("number"),
                id=m.group("id"),
                title=" ".join(m.group("title").split()),
                authors=author_list,
                abstract="",
            )
        )

    return entries
