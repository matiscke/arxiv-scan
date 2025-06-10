import datetime
import logging
import sys
from argparse import ArgumentParser

from . import __version__
from .config import (Config, configfile_default_location, file_editor,
                     find_configfile, load_config_legacy_format)
from .entry_evaluation import evaluate_entries, sort_entries
from .output import print_entries
from .parse import get_entries, submission_window_start
from .categories import category_map


logger = logging.getLogger(__name__)


def parse_cli_arguments() -> tuple:
    """Definition and parsing of command line arguments"""
    parser = ArgumentParser()
    parser.add_argument("--config", metavar="/path/to/config",
                        help="Path to configuration file (check README for defaults)")
    parser.add_argument("--default-config", nargs="?", default=False, const=True, metavar="/path/to/config",
                        help="Write default config to default location (or specified path)")
    parser.add_argument("--config-convert", nargs="?", default=False, const=True, metavar="/path/to/config",
                        help="Convert authors and keywords config from legacy format")
    parser.add_argument("--edit", action="store_true",
                        help="Edit config in default text editor")
    parser.add_argument("-d", "--date", default=None,
                        help='"new", or "recent", number of days in the past, "YYYY-MM" or "YYYY-MM-DD". Defaults to "new"')
    parser.add_argument("-l", "--len", dest="length", type=int, default=None,
                        help="length of result list, all is -1")
    parser.add_argument("-v", "--rating", type=int, default=None,
                        help="minimum rating for result list")
    parser.add_argument("-c", "--categories", default=None,
                        help="arXiv subjects to scan, comma seperated list")
    parser.add_argument("--reverse", action="store_true", default=None,
                        help="reverse list (lowest ranked paper on top)")
    parser.add_argument("--only-resubmissions", action="store_true", default=None,
                        help="Show only resubmissions")
    parser.add_argument("--ignore-cross-lists", action="store_true", default=None,
                        help="Ignore cross-lists")
    parser.add_argument("--ignore-abstract", action="store_true", default=None,
                        help="Ignore abstract in rating")
    parser.add_argument("--log", choices=["info", "debug"], default="warning",
                        help="Set loglevel")
    parser.add_argument("--version", action="version",
                        version="%(prog)s {}".format(__version__))

    return parser.parse_args()


def main():
    args = parse_cli_arguments()

    logging.basicConfig(level=getattr(logging, args.log.upper()))

    # write default config
    if args.default_config:
        if args.default_config is True:
            path = configfile_default_location(mkdir=True)
        else:
            path = args.default_config
        config = Config()
        config.write(path)
        print("Written default config to {}".format(path))
        sys.exit()

    # convert legacy config into new format
    if args.config_convert:
        if args.config_convert is True:
            path = configfile_default_location(mkdir=True)
        else:
            path = args.config_convert
        config = load_config_legacy_format("keywords.txt", "authors.txt")
        config.write(path)
        print("Convert legacy configuration to {}".format(path))
        sys.exit()

    # Open config file in text editor
    if args.edit:
        try:
            path = find_configfile()
        except FileNotFoundError:
            if input("No config file found. Create at default location? [y/N] ").lower() == "y":
                path = configfile_default_location(mkdir=True)
                Config().write(path)
            else:
                print("No file to edit. Exiting")
                sys.exit(1)
        file_editor(path)
        sys.exit()

    # read config
    config = Config()
    if args.config:
        configfile = args.config
    else:
        try:
            configfile = find_configfile()
        except FileNotFoundError:
            logger.error("Cannot find config file. Check Readme for configuration locations")
            sys.exit(1)

    config.read(configfile)
    logger.info("Reading configuration from file '%s'", configfile)

    # overwrite config from CLI arguments
    config["date"] = args.date
    config["length"] = args.length
    config["minimum_rating"] = args.rating
    config["categories"] = args.categories
    config["reverse_list"] = args.reverse
    config["only_resubmissions"] = args.only_resubmissions
    config["show_cross_lists"] = (
        not args.ignore_cross_lists if args.ignore_cross_lists is not None else None
    )
    config["ignore_abstract"] = args.ignore_abstract

    # parse date string
    if config["date"] == "new" or config["date"] is None:
        cutoff_date = submission_window_start(datetime.datetime.now().astimezone())
    elif config["date"] == "recent":
        cutoff_date = submission_window_start(
            datetime.datetime.now().astimezone() - datetime.timedelta(days=6)
        )
    elif isinstance(config["date"], int):
        cutoff_date = (
            datetime.datetime.now().astimezone().replace(hour=0, minute=0,second=0, microsecond=0)
            - datetime.timedelta(days=config["date"])
        )
    else:
        try:
            cutoff_date = datetime.datetime.strptime(config["date"], "%Y-%m").astimezone()
        except ValueError:
            try:
                cutoff_date = datetime.datetime.strptime(config["date"], "%Y-%m-%d").astimezone()
            except ValueError:
                raise ValueError("Couldn't parse parameter 'date' from argument or config file") from None

    print(f"Getting Submissions since {cutoff_date}")

    # parse categories
    categories = config["categories"].split(",")
    for category in categories:
        categories.extend(category_map.get(category, ()))

    try:
        entries = get_entries(
            categories, cutoff_date=cutoff_date,
            cross_lists=config["show_cross_lists"],
            resubmissions=config["only_resubmissions"]
        )
    except Exception as e:
        print("Error while fetching feed:")
        print(repr(e))
        sys.exit(1)

    evaluate_entries(entries, keyword_ratings=config.keywords,
                     author_ratings=config.authors, rate_abstract=not config["ignore_abstract"])
    entries = sort_entries(
        entries,
        rating_min=config["minimum_rating"],
        reverse=config["reverse_list"],
        length=config["length"],
    )
    print_entries(entries)


if __name__ == "__main__":
    main()
