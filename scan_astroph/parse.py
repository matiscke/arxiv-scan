"""Functions relating to parsing Arxiv.org"""
import feedparser
from datetime import datetime

from .entry_evaluation import Entry


def linebreak_fix(text: str):
    """Replace linebreaks and indenting with single space"""
    return " ".join(line.strip() for line in text.split("\n"))


def atom2entry(entry: feedparser.util.FeedParserDict) -> Entry:
    """Convert entry from API object to Entry object"""
    return Entry(
        id=entry.id.split("/")[-1],
        title=linebreak_fix(entry.title),
        authors=[author["name"] for author in entry.authors],
        abstract=linebreak_fix(entry.summary),
        category=entry.arxiv_primary_category["term"],
        date_submitted=datetime.fromisoformat(entry.published[:-1]),
        date_updated=datetime.fromisoformat(entry.updated[:-1]),
    )


def get_entries(
    categories: list,
    cutoff_date: datetime,
    cross_lists: bool = True,
    resubmissions: bool = False,
) -> list:
    """Get arXiv submissions from now back to cutoff_date

    Args:
        categories (list): List of arXiv subjects (e.g. `astr-ph.EP`)
        cutoff_date (datetime.datetime): Get submissions since this date
        cross_lists (:obj:`bool`, optional): Include cross-lists (default: True)
        resubmissions (:obj:`bool`, optional): Inlcude resubmissions (default: False)

    Returns:
        list of Entry
    """
    # set results per API request to 10 per day (min 15, max 1000)
    days_since_cutoff = round((datetime.now() - cutoff_date).total_seconds() / 86400)
    max_results = min(max(days_since_cutoff * 10, 15), 1000)

    sortby = "lastUpdatedDate" if resubmissions else "submittedDate"

    category_str = ",".join(categories)

    entries = []
    # Extract entries, make multiple requests if more than max_results entries
    start = 0
    finished = False
    while not finished:
        feed = feedparser.parse(
            "https://export.arxiv.org/api/query?search_query="
            f"cat:{category_str}&sortBy={sortby}&sortOrder=descending"
            f"&start={start}&max_results={max_results}"
        )

        for feedentry in feed.entries:
            entry = atom2entry(feedentry)
            # stop if cutoff date is reached
            if entry.date_submitted < cutoff_date:
                finished = True # mark outer loop finished
                break

            if not cross_lists and entry.category not in categories:
                continue
            entries.append(entry)

        # new startpoint for next request
        start += max_results

    return entries
