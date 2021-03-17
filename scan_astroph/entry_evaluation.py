"""Definition of class Entry and all evaluation related functions"""
import re

from .config import AUTHORS, TITLE_KEYWORDS


class Entry(object):
    ''' This class represents one arxiv entry'''
    def __init__(self, number, id, title, authors, abstract):
        self.number = int(number)
        self.id = id
        self.title = title
        self.authors = authors
        self.abstract = abstract
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

def evaluate_entries(entries):
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

        for au, val in AUTHORS.items():
            au = au.lower()
            for i, a in enumerate(entry.authors):
                counts = a.lower().count(au)
                if counts > 0:
                    entry.mark_author(i)
                    rating = counts * val
                    entry.rating += rating

def sort_entries(entries, rating_min, reverse, length):
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

    results = sorted(entries, key=lambda x: x.rating, reverse=True)
    step = 1 if reverse else -1
    return results[0:length][::step]
