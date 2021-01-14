#!/usr/bin/env python

from __future__ import division, absolute_import, print_function, unicode_literals

import re

ARXIV_BASE = 'https://arxiv.org/list/astro-ph.EP'
DEBUG = False
# CAFILE = '/afs/mpa/home/rglas/software/cert/arxiv.org.crt'
TITLE_KEYWORDS = {
        'Supernova': 3,
        'Core-Collapse': 2,
        'Core': 1, # core is often found
        'Collapse': 1,
        'Explosion': 2,
        'Mechanism': 2,
        'Merger': 2,
        'Rotation': 1,
        'Two-Moment': 5,
        'Moment': 1, # moment is often found (momentum)
        'Ray-by-Ray': 5,
        'Multi-Dimensional': 3,
        'Three-Dimensional': 4,
        'Three': 1,
        'SASI': 4,
        'LESA': 5,
        'Neutrino': 5,
        'Flavor': 2,
        'Flavour': 2,
        'Oscillation': 2,
        'Transport': 4,
        'Simulation': 3,
        'Equation of State': 2,
        'Gravitational Wave': 1,
        'Nucleosynthesis': 1,
        'Massive': 1,
        'Star': 1,
        }
AUTHORS = {
        'Janka': 5,
        'Couch': 4,
        'Connor': 5,  # O'Connor
        'Ott': 1, # Ott is often found
        'Abdikamalov': 2,
        'Sullivan': 2,
        'Burrows': 5,
        'Sumiyoshi': 4,
        'Skinner': 5,
        'Vartanyan': 5,
        'Dolence': 4,
        'Bollig': 4,
        'Ertl': 4,
        'Just': 5,
        'Obergaulinger': 4,
        'Andresen': 3,
        'Roberts': 5,
        'Radice': 4,
        'Tamborra': 3,
        'Kotake': 3,
        'Kuroda': 3,
        'Takiwaki': 3,
        'Nakamura': 3,
        'Takahashi': 3,
        'Nagakura': 3,
        'Mirizzi': 3,
        'Langer': 3,
        'Fischer': 3,
        'Heger': 2,
        'Woosley': 3,
        'Walk': 1,
        'Powell': 1,
        'Soker': 3,
          }
REGEX = \
r'''<dt><a name="item(\d+)">.*<span class="list-identifier"><a href="/abs/([0-9.]*)".*</span></dt>
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

def debug_print(*msg):
    ''' Print only in DEBUG mode '''
    if DEBUG:
        print('[DEBUG]', *msg)

class Entry(object):
    ''' This class represents one arxiv entry'''
    def __init__(self, number, id, title, authors, abstract):
        self.number = int(number)
        self.id = id
        def clear(s):
            return s.strip().replace('  ', ' ').replace('&#x27;', "'")
        self.title = clear(title)
        self.authors = []
        for a in authors:
            self.authors.append(clear(a))
        self.abstract = clear(abstract)
        self.rating = 0
        self.title_marks = []
        self.author_marks = [False for a in self.authors]
    def mark_title_position(self, position):
        ''' Mark title at given position'''
        self.title_marks.append(position)
    def mark_title_keyword(self, kw):
        ''' Mark title at positions where kw is found'''
        counts = self.title.lower().count(kw)
        for i in range(counts):
            starts = [m.start() for m in re.finditer(kw, self.title.lower())]
            ends = [m.end() for m in re.finditer(kw, self.title.lower())]
            for s, e in zip(starts, ends):
                for pos in range(s, e):
                    self.mark_title_position(pos)
    def mark_author(self, number):
        ''' Mark author (by given number in author list)'''
        self.author_marks[number] = True

def load(address):
    ''' Load content from website'''
    kwargs = {}
    try:
        from urllib.request import urlopen # python 3
        from ssl import create_default_context
        # DeprecationWarning: cafile, capath and cadefault are deprecated
        # kwargs['context'] = create_default_context(cafile=CAFILE)
    except ImportError:
        from urllib2 import urlopen # python 2
        # kwargs['cafile'] = CAFILE
    f = urlopen(address, **kwargs)
    return f.read()

def scan(data):
    ''' Scan content and retrieve entries

    We use regular expressions REGEX and REGEX_AUTHORS.
    The return value is a list containing Entry objects.
    '''
    entries = []
    m = re.search(REGEX, data.decode())
    while m is not None:
        authors = m.group(4)
        debug_print(m.group(1), m.group(3))
        m_au = re.findall(REGEX_AUTHORS, authors)
        entries.append(Entry(number=m.group(1),
                        id=m.group(2),
                        title=m.group(3),
                        authors=m_au,
                        abstract=''))
        data = data[m.end():]
        m = re.search(REGEX, data.decode())
    debug_print('First entry:', entries[0].id)
    debug_print('Last  entry:', entries[-1].id)
    return entries

def evaluate(entries):
    ''' Evaluate entries

    Rate entries according to keywords and author list.
    '''
    for entry in entries:
        for kw, val in TITLE_KEYWORDS.items():
            kw = kw.lower()
            counts = entry.title.lower().count(kw)
            if counts > 0:
                entry.mark_title_keyword(kw)
                rating = counts * val
                entry.rating += rating
                debug_print('{:3d} points for {:10.10} in title {:40.40}'.format(
                    rating, kw, entry.title))
        for au, val in AUTHORS.items():
            au = au.lower()
            for i, a in enumerate(entry.authors):
                counts = a.lower().count(au)
                if counts > 0:
                    entry.mark_author(i)
                    rating = counts * val
                    entry.rating += rating
                    debug_print('{:3d} points for {:10.10} in author {:40.40}'.format(
                        rating, au, a))
        debug_print('number, rating', entry.number, entry.rating)
    debug_print('First entry (after evaluating):', entries[0].rating)
    debug_print('Last  entry (after evaluating):', entries[-1].rating)

def sort(entries, rating_min, reverse, length):
    ''' Sort entries by rating

    Only entries with rating >= rating_min are
    listed, and the list is at maximum length
    entries long.
    If reverse is True, the entries are reversed
    (after cutting the list to length entries).
    '''
    if length < 0:
        length = None
    for i in range(len(entries)-1, -1, -1):
        if entries[i].rating < rating_min:
            del entries[i]
    debug_print('number of entries with value > min:', len(entries))
    results = sorted(entries, key=lambda x: x.rating, reverse=True)
    step = 1 if reverse else -1
    return results[0:length][::step]

def show(entries):
    ''' Print all entries'''
    try:
        from termcolor import colored
    except ImportError:
        def colored(s, *args, **kwargs):
            return s
    for i, entry in enumerate(entries):
        debug_print()
        debug_print('({value:2d})  https://arxiv.org/abs/{id:10.10s}  [{num:4d}]'.format(
                      value=entry.rating, id=entry.id, num=entry.number))
        debug_print('"{authors:s}"'.format(authors=', '.join(entry.authors)))
        debug_print('"{title:s}"'.format(title=entry.title))
        debug_print(repr(entry.title))

        rating = colored('({:2d})'.format(entry.rating), 'green')
        authors = []
        authors_len = 0
        for i, a in enumerate(entry.authors):
            if authors_len + len(a) > 90:
                authors.append(colored('...', attrs=['underline']))
                break
            authors_len += len(a)
            if entry.author_marks[i]:
                authors.append(colored(a, 'red', attrs=['underline']))
            else:
                authors.append(colored(a, attrs=['underline']))
        authors = colored(', ', attrs=['underline']).join(authors)
        title_lines = [[]]
        title_len = 0
        for i, t in enumerate(entry.title):
            if t == ' ' and title_len > 90:
                title_len = 0
                title_lines.append([])
                continue
            title_len += 1
            if i in entry.title_marks:
                title_lines[-1].append(colored(t, 'blue'))
            else:
                title_lines[-1].append(t)
        title_lines = [''.join(t) for t in title_lines]

        print('{rating:s} {arxiv:s}{id:s}'.format(
            rating=rating,
            arxiv=colored('https://arxiv.org/abs/', 'green'),
            id=colored(entry.id, 'green')))
        print('     {authors:s}'.format(authors=authors))
        for line in title_lines:
            print('     {title:s}'.format(title=line))

def main():
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-d', '--date', dest='date',
            help='date in format yyyy-mm', default=None)
    parser.add_option('-l', '--len', dest='length',
            help='length of result list, all is -1', default=20)
    parser.add_option('-v', '--rating', dest='rating',
            help='minumim rating for result list', default=5)
    parser.add_option('--reverse', dest='reverse',
            help='reverse list', action='store_true', default=False)
    parser.add_option('--debug', dest='debug',
            help='debug', action='store_true', default=False)
    (options, args) = parser.parse_args()

    if options.debug:
        global DEBUG
        DEBUG = True

    if options.date is None:
        address = '{base:s}/new'.format(base=ARXIV_BASE)
    else:
        year, month = options.date.split('-')
        year = year[2:4] if len(year) == 4 else year
        address = '{base:s}/{year:2.2s}{month:2.2s}?show=3000'.format(
                base=ARXIV_BASE, year=year, month=month)

    debug_print('using arxiv address:', address)
    data = load(address)

    if DEBUG:
        with open('debug_file_content.txt', 'w') as outfile:
            outfile.write(data)
        debug_print('written data to file: debug_file_content.txt')

    entries = scan(data)
    evaluate(entries)
    entries = sort(entries, rating_min=int(options.rating),
            reverse=options.reverse, length=int(options.length))
    show(entries)

if __name__ == '__main__':
    main()
