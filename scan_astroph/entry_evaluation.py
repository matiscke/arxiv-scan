"""Definition of class Entry and all evaluation related functions"""
import re


class Entry(object):
    """This class represents one arxiv entry"""

    def __init__(self, number: int, id: str, title: str,
                 authors: list, abstract: str):
        self.number = int(number)
        self.id = id
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.rating = 0
        self.title_marks = []
        self.author_marks = [False] * len(self.authors)

    def mark_title_position(self, position: int) -> None:
        """Mark title at given position"""
        self.title_marks.append(position)

    def mark_title_keyword(self, keyword: str) -> None:
        """Mark title at positions where keyword is found"""
        counts = self.title.lower().count(keyword)
        for _ in range(counts):
            starts = [m.start() for m in re.finditer(keyword, self.title.lower())]
            ends = [m.end() for m in re.finditer(keyword, self.title.lower())]
            for s, e in zip(starts, ends):
                for pos in range(s, e):
                    self.mark_title_position(pos)

    def mark_author(self, number: int) -> None:
        """Mark author (by given number in author list)"""
        self.author_marks[number] = True


def evaluate_entries(entries: list, keyword_ratings: dict, author_ratings: dict) -> list:
    ''' Evaluate entries

    Rate entries according to keywords and author list.
    Args:
        entries (list[Entry]): entries to evaluate. Entry.rating will be modified
        keywords (dict): dict with keywords as keys and rating as value
        authors (dict): dict with authors as keys and rating as value

    Returns:
        list[Entry]: input entries with rating attached (same object as input list)
    '''
    for entry in entries:
        for keyword, rating in keyword_ratings.items():
            keyword = keyword.lower()
            counts = entry.title.lower().count(keyword)
            if counts > 0:
                entry.mark_title_keyword(keyword)
                entry.rating += counts * rating

        for author, rating in author_ratings.items():
            author = author.lower()
            for i, a in enumerate(entry.authors):
                match = re.search(r'\b{}\b'.format(author), a)
                if match:
                    entry.mark_author(i)
                    entry.rating += rating

    return entries


def sort_entries(entries: list, rating_min: int, reverse: bool, length: int) -> list:
    ''' Sort entries by rating

    Only entries with rating >= rating_min are
    listed, and the list is at maximum length
    entries long.
    If reverse is True, the entries are reversed
    (after cutting the list to length entries).
    '''
    if length < 0:
        length = None

    # remove entries with low rating
    entries_filtered = filter(lambda entry: entry.rating >= rating_min, entries)
    # sort by rating
    results = sorted(entries_filtered, key=lambda x: x.rating, reverse=reverse)

    return results[:length]
