"""Functions relating to parsing Arxiv.org"""
from datetime import datetime, timedelta
from xml.etree import ElementTree

import urllib
import urllib.request
import time
import logging
import pytz

from .entry_evaluation import Entry
from .oai_api import namespaces, base_url, attempts, delay


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

def xml2entry(record: ElementTree.Element, namespaces: dict) -> Entry:
    """Convert entry from an XML object to an Entry object"""
    identifier = record.find('./oai:header/oai:identifier', namespaces=namespaces).text
    categories = record.findall('./oai:header/oai:setSpec', namespaces=namespaces)
    title = record.find('./oai:metadata/arxivraw:arXivRaw/arxivraw:title', namespaces=namespaces).text
    authors = record.find('./oai:metadata/arxivraw:arXivRaw/arxivraw:authors', namespaces=namespaces).text
    abstract = record.find('./oai:metadata/arxivraw:arXivRaw/arxivraw:abstract', namespaces=namespaces).text
    versions = record.findall('./oai:metadata/arxivraw:arXivRaw/arxivraw:version', namespaces=namespaces)
    dates = []
    for version in versions:
        dates.append(version.find('./arxivraw:date', namespaces=namespaces).text)
    return Entry(
        id=identifier.split(":")[-1],
        title=linebreak_fix(title),
        authors=[author.strip() for author in authors.split(',')],
        abstract=linebreak_fix(abstract),
        category=categories[0].text,
        date_submitted=pytz.utc.localize(datetime.strptime(dates[0], "%a, %d %b %Y %H:%M:%S %Z")),
        date_updated=pytz.utc.localize(datetime.strptime(dates[-1], "%a, %d %b %Y %H:%M:%S %Z")),
    )

def get_entries(
    categories: list,
    cutoff_date: datetime,
    cross_lists: bool = True,
    resubmissions: bool = False,
) -> list:
    """Get arXiv submissions from now back to cutoff_date

    Args:
        categories (list): List of arXiv subjects (e.g. `physics:astro-ph:EP`)
        cutoff_date (datetime.datetime): Get submissions since this date
        cross_lists (:obj:`bool`, optional): Include cross-lists (default: True)
        resubmissions (:obj:`bool`, optional): Show also resubmissions (default: False)

    Returns:
        list of Entry
    """

    entries = []

    date_from = cutoff_date.strftime("%Y-%m-%d")

    for category in categories:

        category_url = urllib.parse.quote(category)
        url = f"{base_url:s}?verb=ListRecords&metadataPrefix=arXivRaw&from={date_from:s}&set={category_url:s}"
        skip = 0

        while True:
            logger.debug(f'Query: {url:s}')

            for i in range(attempts):
                try:
                    xml_data = urllib.request.urlopen(url)
                except urllib.error.HTTPError as err:
                    if err.code == 503:
                        timeout = int(err.headers['Retry-After'])
                        time.sleep(timeout)
                    else:
                        raise err
                else:
                    with xml_data:
                        tree = ElementTree.parse(xml_data)
                    break

            root = tree.getroot()
            records = root.findall("./oai:ListRecords/oai:record", namespaces=namespaces)

            if len(records) == 0:
                break

            for r, record in enumerate(records):

                if r < skip:
                    continue

                entry = xml2entry(record, namespaces)

                if not cross_lists:
                    if not entry.category.startswith(category):
                        # the following matches indicate that it's NOT crossref
                        # "physics:astro-ph:EP" startswith "physics"
                        # "physics:astro-ph:EP" startswith "physics:astro-ph"
                        # "physics:astro-ph:EP" startswith "physics:astro-ph:EP"
                        continue  # skip

                if resubmissions:
                    # if resubmissions are allowed: compare last date (update date)
                    if entry.date_updated < cutoff_date:
                        continue  # skip
                else:
                    # if resubmissions are not allowed: compare first date (submission date)
                    if entry.date_submitted < cutoff_date:
                        continue  # skip

                entries.append(entry)

            resumption = root.find("./oai:ListRecords/oai:resumptionToken", namespaces=namespaces)
            if resumption is None:
                break

            resumption = urllib.parse.unquote(resumption.text)
            next_url = resumption.split("&skip=")[0]
            skip = int(resumption.split("&skip=")[1])

            url = f"{base_url:s}?{next_url:s}"
            time.sleep(delay)  # play nice

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
