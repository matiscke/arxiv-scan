"""Functions relating to parsing Arxiv.org"""
import re

from .entry_evaluation import Entry

REGEX_TEMPLATE = \
r'''<dt><a name="item(\d+)">.*<span class="list-identifier"><a href="/abs/([0-9.]*)".*<\/a> {ignore_pattern}.*</span></dt>
<dd>
<div class="meta">
<div class="list\-title mathjax">\s*
<span class="descriptor">Title:</span>\s*(.*)
</div>
<div class="list\-authors">
<span class="descriptor">Authors:</span>\s*
([\s\S]*?)
</div>'''
REGEX_AUTHORS = r'<a href=".*">(.*)</a>.*\n?'

def parse_html(data, cross_lists=True, resubmissions=False):
    ''' Scan content and retrieve entries

    We use regular expressions REGEX and REGEX_AUTHORS.
    The return value is a list containing Entry objects.
    '''
    entries = []
    ignore_pattern = ""
    if not cross_lists:
        ignore_pattern += r'(?!\(cross-list)'
    if not resubmissions:
        ignore_pattern += r'(?!\(replaced)'

    regex = REGEX_TEMPLATE.format(ignore_pattern=ignore_pattern)
    m = re.search(regex, data)
    while m is not None:
        authors = m.group(4)
        m_au = re.findall(REGEX_AUTHORS, authors)
        entries.append(Entry(number=m.group(1),
                        id=m.group(2),
                        title=" ".join(m.group(3).split()),
                        authors=m_au,
                        abstract=''))
        data = data[m.end():]
        m = re.search(regex, data)
    return entries
