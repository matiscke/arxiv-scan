from optparse import OptionParser

from .entry_evaluation import evaluate_entries, sort_entries
from .output import print_entries
from .parse import parse_html
from .tools import load_html

ARXIV_BASE = 'https://arxiv.org/list/astro-ph.EP'

def parse_cli_arguments() -> tuple:
    """Definition and parsing of command line arguments"""
    parser = OptionParser()
    parser.add_option('-d', '--date', dest='date',
            help='date in format yyyy-mm, or "new", or "recent"', default='new')
    parser.add_option('-l', '--len', dest='length',
            help='length of result list, all is -1', default=-1)
    parser.add_option('-v', '--rating', dest='rating',
            help='minimum rating for result list', default=6)
    parser.add_option('--reverse', dest='reverse',
            help='reverse list', action='store_false', default=True)
    parser.add_option('--show-resubmissions', action='store_true', default=False)
    parser.add_option('--ignore-cross-lists', action="store_true", default=False)
    parser.add_option('--debug', dest='debug',
            help='debug', action='store_true', default=False)
    return parser.parse_args()

def main():
    (options, args) = parse_cli_arguments()

    if (options.date == 'new') | (options.date is None):
        address = '{base:s}/new'.format(base=ARXIV_BASE)
        print("querying authors and titles for new submissions (today's listing)")
    elif options.date == 'recent':
        address = '{base:s}/recent'.format(base=ARXIV_BASE)
        print('querying authors and titles for recent submissions')
    else:
        year, month = options.date.split('-')
        year = year[2:4] if len(year) == 4 else year
        address = '{base:s}/{year:2.2s}{month:2.2s}?show=3000'.format(
                base=ARXIV_BASE, year=year, month=month)
        print('querying authors and titles for listings in {:2.2s}/{:2.2s}'.format(month, year))

    data = load_html(address)

    entries = parse_html(data, cross_lists=not options.ignore_cross_lists,
                         resubmissions=options.show_resubmissions)
    evaluate_entries(entries)
    entries = sort_entries(entries, rating_min=int(options.rating),
            reverse=options.reverse, length=int(options.length))
    print_entries(entries)


if __name__ == "__main__":
    main()
