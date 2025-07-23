"""Functions relating to parsing Arxiv.org"""
from datetime import datetime, timedelta

import time
import logging
import feedparser
import pytz

from .entry_evaluation import Entry


logger = logging.getLogger(__name__)


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
        resubmissions (:obj:`bool`, optional): Show only resubmissions (default: False)

    Returns:
        list of Entry
    """

    # note: sortBy=lastUpdatedDate shows ONLY resubmissions because, apparently,
    #       the submission date does not count as "lastUpdatedDate"
    sortby = "lastUpdatedDate" if resubmissions else "submittedDate"

    search_query = "+OR+".join(f"cat:{cat}" for cat in categories)

    # delay between requests: 3 seconds is recommended by the arxiv API,
    # but we try less before increasing the delay time
    delay = 0.5
    delay_min = 0.5
    delay_max = 4.0

    # number of requested results: should not be more than 1000 (see arxiv API)
    # but it seems that the server (at the moment?) likes 800 better
    max_results = 800

    num_errors = 0
    max_errors = 100  # exit program when too many errors occur

    entries = []
    # Extract entries, make multiple requests if more than max_results entries
    start = 0
    finished = False
    while not finished and num_errors <= max_errors:
        arxiv_url = (
            f"https://export.arxiv.org/api/query?search_query={search_query}"
            f"&sortBy={sortby}&sortOrder=descending"
            f"&start={start}&max_results={max_results}"
        )

        feed = feedparser.parse(arxiv_url)

        logger.debug(f'Query: {arxiv_url:s}')
        logger.debug(f'Encountered {num_errors:3d} errors so far and delay time is currently {delay:3.1f} seconds')

        # handle errors
        if feed.bozo:
            if isinstance(feed.bozo_exception.reason, ConnectionResetError):
                logger.debug('Try again after ConnectionResetError: [Errno 104] Connection reset by peer')
                num_errors += 1
                delay = min(delay*2, delay_max)
                time.sleep(delay)
                continue  # try again
            else:
                raise feed.bozo_exception

        if len(feed.entries) == 0:
            # a response with no entries indicates a problem with the API response;
            # only if the cutoff date was so far in the past that we ask for ALL
            # entries in a category, this would lead to an infinite loop here,
            # which we hopefully avoid by limiting all requests to 2 years
            num_errors += 1
            delay = min(delay*2, delay_max)
            time.sleep(delay)
            continue  # try again

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
        # note: the number of feed entries might be < max_results
        #       because of incomplete server replies
        start += len(feed.entries)

        if len(feed.entries) < max_results:
            # we obtained less data than requested
            num_errors += 1
            delay = min(delay*2, delay_max)
        else:
            # everything OK
            delay = max(delay/2, delay_min)

        # play nice and sleep a bit (and the server replies are more stable)
        time.sleep(delay)

    if num_errors > max_errors:
        raise IOError('Could not retreive data because of too many errors with the arxiv API')

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
