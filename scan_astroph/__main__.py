import logging
from argparse import ArgumentParser

from . import __version__
from .config import AUTHORS, TITLE_KEYWORDS
from .entry_evaluation import evaluate_entries, sort_entries
from .output import print_entries
from .parse import parse_html
from .tools import load_html

ARXIV_BASE = 'https://arxiv.org/list/astro-ph.EP'

def parse_cli_arguments() -> tuple:
    """Definition and parsing of command line arguments"""
    parser = ArgumentParser()
    parser.add_argument('-d', '--date', dest='date',
            help='date in format yyyy-mm, or "new", or "recent"', default='new')
    parser.add_argument('-l', '--len', dest='length', type=int,
            help='length of result list, all is -1', default=-1)
    parser.add_argument('-v', '--rating', dest='rating', type=int,
            help='minimum rating for result list', default=6)
    parser.add_argument('--reverse', dest='reverse',
            help='reverse list', action='store_false', default=True)
    parser.add_argument('--log', choices=["info", "debug"], default="warning", help="Set loglevel")
    parser.add_argument('--show-resubmissions', action='store_true', default=False)
    parser.add_argument('--ignore-cross-lists', action="store_true", default=False)
    parser.add_argument('--version', action='version',
            version='%(prog)s {}'.format(__version__))
    return parser.parse_args()

def main():
    args = parse_cli_arguments()

    logging.basicConfig(level=getattr(logging, args.log.upper()))

    if (args.date == 'new') | (args.date is None):
        address = '{base:s}/new'.format(base=ARXIV_BASE)
        print("querying authors and titles for new submissions (today's listing)")
    elif args.date == 'recent':
        address = '{base:s}/recent'.format(base=ARXIV_BASE)
        print('querying authors and titles for recent submissions')
    else:
        year, month = args.date.split('-')
        year = year[2:4] if len(year) == 4 else year
        address = '{base:s}/{year:2.2s}{month:2.2s}?show=3000'.format(
                base=ARXIV_BASE, year=year, month=month)
        print('querying authors and titles for listings in {:2.2s}/{:2.2s}'.format(month, year))

    data = load_html(address)

    entries = parse_html(data, cross_lists=not args.ignore_cross_lists,
                         resubmissions=args.show_resubmissions)
    evaluate_entries(entries, keyword_ratings=TITLE_KEYWORDS, author_ratings=AUTHORS)
    entries = sort_entries(entries, rating_min=args.rating,
            reverse=args.reverse, length=args.length)
    print_entries(entries)


if __name__ == "__main__":
    main()
