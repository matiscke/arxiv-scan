"""Definition of class Entry and all evaluation related functions"""
import re
from datetime import datetime


class Entry(object):
    """This class represents one arxiv entry"""

    def __init__(self, id: str, title: str,
                 authors: list, abstract: str, category: str = "",
                 date_submitted: datetime = None,
                 date_updated: datetime = None,
                 number: int = None):
        self.id = id
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.category = category
        self.date_submitted = date_submitted
        self.date_updated = date_updated

        self.title_marks = []
        self.author_marks = [False] * len(self.authors)

        self.rating = None
        self.detailed_ratings = {}

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(\n    id={self.id!r},\n    title={self.title!r},\n    "
            f"authors={self.authors!r},\n    abstract={self.abstract!r},\n    "
            f"category={self.category!r},\n    "
            f"date_submitted={self.date_submitted!r},\n    date_updated={self.date_updated!r}"
            "\n)"
        )

    def mark_title_position(self, position: int) -> None:
        """Mark title at given position"""
        self.title_marks.append(position)

    def mark_title_keyword(self, keyword: str) -> None:
        """Mark title at positions where keyword is found"""
        title_lower = self.title.lower()
        for match in re.finditer(re.escape(keyword), title_lower):
            for pos in range(match.start(), match.end()):
                self.mark_title_position(pos)

    def mark_author(self, number: int) -> None:
        """Mark author (by given number in author list)"""
        self.author_marks[number] = True

    def evaluate(self, keyword_ratings: dict, author_ratings: dict,
                       rate_abstract: bool=True) -> int:
        """Evaluate entry

        Rate entries according to keywords and author list.
        This sets the rating attribute and marks title and marks title words and authors.

        Args:
            keywords (dict): dict with keywords as keys and rating as value
            authors (dict): dict with authors as keys and rating as value
        Returns:
            int: rating for this entry
        """
        # find keywords in title and abstract
        for keyword, rating in keyword_ratings.items():
            keyword = keyword.lower()
            # find and mark keyword in title
            counts = self.title.lower().count(keyword)
            if counts > 0:
                self.mark_title_keyword(keyword)
                self.detailed_ratings[keyword] = counts * rating
            # find keyword in abstract
            if rate_abstract:
                counts = self.abstract.lower().count(keyword)
                if counts > 0:
                    try:
                        self.detailed_ratings[keyword] += counts * rating
                    except KeyError:
                        self.detailed_ratings[keyword] = counts * rating

        # find authors
        for author, rating in author_ratings.items():
            for i, a in enumerate(self.authors):
                match = re.search(r'\b{}\b'.format(author), a, flags=re.IGNORECASE)
                if match:
                    self.mark_author(i)
                    self.detailed_ratings[author] = rating
                    break  # count each author only once

        self.rating = sum(self.detailed_ratings.values())
        return self.rating

def evaluate_entries(entries: list, keyword_ratings: dict, author_ratings: dict, rate_abstract: bool=True) -> list:
    """Evaluate all entries in list"""
    for entry in entries:
        entry.evaluate(keyword_ratings, author_ratings, rate_abstract)

def sort_entries(entries: list, rating_min: int, reverse: bool, length: int) -> list:
    ''' Sort entries by rating

    Only entries with rating >= rating_min are listed, and the list is at
    maximum length entries long. If reverse is True, the entries are reversed
    (after cutting the list to length entries). Note that the default order
    is most relevant paper on top.
    '''
    if length < 0:
        length = None

    # remove entries with low rating
    entries_filtered = filter(lambda entry: entry.rating >= rating_min, entries)
    # sort by rating
    results = sorted(entries_filtered, key=lambda x: x.rating, reverse=not reverse)

    return results[:length]
