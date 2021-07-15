"""Functions relating to parsing Arxiv.org"""
from datetime import datetime, timedelta

import feedparser
import pytz

from .entry_evaluation import Entry


def linebreak_fix(text: str):
    """Replace linebreaks and indenting with single space"""
    return " ".join(line.strip() for line in text.split("\n"))

def datetime_fromisoformat(datestr: str):
    """Convert iso formatted datetime string to datetime object

    This is only needed for compatibility, as datetime.fromisoformat()
    was added in Python 3.7
    """
    return datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S")

def atom2entry(entry: feedparser.util.FeedParserDict) -> Entry:
    """Convert entry from API object to Entry object"""
    return Entry(
        id=entry.id.split("/")[-1],
        title=linebreak_fix(entry.title),
        authors=[author["name"] for author in entry.authors],
        abstract=linebreak_fix(entry.summary),
        category=entry.arxiv_primary_category["term"],
        date_submitted=pytz.utc.localize(datetime_fromisoformat(entry.published[:-1])),
        date_updated=pytz.utc.localize(datetime_fromisoformat(entry.updated[:-1])),
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
    days_since_cutoff = round(
        (datetime.now().astimezone() - cutoff_date) / timedelta(days=1)
    )
    max_results = min(max(days_since_cutoff * 10, 15), 1000)

    sortby = "lastUpdatedDate" if resubmissions else "submittedDate"

    search_query = "+OR+".join(f"cat:{cat}" for cat in categories)

    entries = []
    # Extract entries, make multiple requests if more than max_results entries
    start = 0
    finished = False
    while not finished:
        feed = feedparser.parse(
            f"https://export.arxiv.org/api/query?search_query={search_query}"
            f"&sortBy={sortby}&sortOrder=descending"
            f"&start={start}&max_results={max_results}"
        )

        if len(feed.entries) == 0:
            break
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


def submission_window_start(date: datetime, tz=pytz.timezone("US/Eastern")):
    """Find start of latest submission window of arxiv.org

    Submission window reference: https://arxiv.org/help/availability

    Args:
        date (datetime): localized datetime to evaluate for submission window start
        tz (tzinfo): timezone for publishing times

    Returns:
        datetime: localized datetime at start of last published submission window
    """
    date_tz = date.astimezone(tz)
    weekday = date_tz.weekday()

    # offset between current weekday and submission window start
    offset_map = {0: 4, 1: 4, 2: 2, 3: 2, 4: 2, 5: 3, 6: 4}
    # no publishing on Friday and Saturday
    if weekday not in (4, 5) and date_tz.hour >= 20:
        weekday = (weekday + 1) % 7
        offset = offset_map[weekday] - 1
    else:
        offset = offset_map[weekday]

    return date_tz.replace(hour=14, minute=0, second=0, microsecond=0) - timedelta(
        days=offset
    )
