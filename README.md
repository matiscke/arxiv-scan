arxiv-scan
=============
Scan abstract listings on ArXiV for keywords and favorite authors in your categories to distill a list of papers most relevant for *you*.
Keywords can be typed in manually or be found by ranking word occurrences in a provided file (e.g., a `.bib` file).

*arxiv-scan* was created by [Robert Glas](https://github.com/rmglas), [Simeon Doetsch](https://github.com/Simske), and [Martin Schlecker](https://github.com/matiscke).

# Installation
Requirements: Python >=3.5

## Using pip 
We recommend to install the latest stable version of *arxiv-scan* using pip (or [pipx](https://pypa.github.io/pipx/) for an isolated environment):
```
pip install arxiv-scan
```
:information_source:  Depending on your Python installation, you might instead need `pip3 install arxiv-scan` or `python3 -m pip install arxiv-scan`.

## From source
*arxiv-scan* is being developed on github. If you feel like hacking, feel free to install the latest version from there:
```
pip install --upgrade git+https://github.com/matiscke/arxiv-scan.git
```



# Usage
## Query today's arXiV listing for relevant papers
First setup your keywords and authors (see configuration section),
then just run `arxiv-scan` (or `python -m arxiv_scan`) to get the relevant listings.

## Command line reference
```
usage: arxiv-scan [-h] [--config /path/to/config] [--default-config [/path/to/config]]
                  [--config-convert [/path/to/config]] [--edit] [-d DATE] [-l LENGTH]
                  [-v RATING] [-c CATEGORIES] [--reverse] [--show-resubmissions]
                  [--ignore-cross-lists] [--ignore-abstract] [--log {info,debug}]
                  [--version]

optional arguments:
  -h, --help            show this help message and exit
  --config /path/to/config
                        Path to configuration file (check README for defaults)
  --default-config [/path/to/config]
                        Write default config to default location (or specified path)
  --config-convert [/path/to/config]
                        Convert authors and keywords config from legacy format
  --edit                Edit config in default text editor
  -d DATE, --date DATE  "new", or "recent", number of days in the past, "YYYY-MM" or
                        "YYYY-MM-DD". Defaults to "new"
  -l LENGTH, --len LENGTH
                        length of result list, all is -1
  -v RATING, --rating RATING
                        minimum rating for result list
  -c CATEGORIES, --categories CATEGORIES
                        arXiv subjects to scan, comma separated list
  --reverse             reverse list (lowest ranked paper on top)
  --show-resubmissions  Include resubmissions
  --ignore-cross-lists  Include cross-lists
  --ignore-abstract     Ignore abstract in rating
  --log {info,debug}    Set loglevel
  --version             show program's version number and exit
```
# Configuration
In the configuration file all the keywords and authors have to be set, as well as other optional configuration.

The easiest way to get started is to run `arxiv-scan --edit`, this will open the configuration file in the
default text editor.

Alternatively create a default configfile with `arxiv-scan --default-config`, and edit it manually.

arXiv topics can be selected with the `categories` option, it accepts a comma-separated list of topics.
[List of topics](https://arxiv.org/category_taxonomy)
## Configuration format:
```ini
[authors]
# author = rating
Alpher = 1
Bethe = 2
Gamov = 3

[keywords]
# keyword = rating
star = 1
planet = 2
habitable = 3

[options]
# other options (can also be set on CLI)
# default is used if ommited
categories = astro-ph.EP
date = new
length = -1
minimum_rating = 10 
reverse_list = False
show_resubmissions = False
show_cross_lists = True
```

## Automatically extract keywords from a file (e.g. one with bibtex entries):
- Run `arxiv-scan.wordcounter file_to_scan` (or `python -m scan_astroph.wordcounter file_to_scan`).
It scans the text file and extracts words with 4-12 characters from it, sorted by occurrence in the file.
- You will be asked to rank these suggested keywords. For each word shown, press 'Enter' to reject it or provide an integer rating, e.g., from 1 to 5 (higher=more relevant). Conclude by pressing `C`.
- Manually insert particularly important authors into the config file (e.g. with `arxiv-scan --edit`)

## Configuration locations:
`arxiv-scan` searches the these paths for the config file, and loads the first found:
- from environment variable: `$ARXIV_SCAN_CONF`
- from home directory: `~/.arxiv-scan.conf`
- default path (platform dependent):
  - on Linux / Unix (except MacOS): `$XDG_CONFIG_HOME/arxiv-scan/arxiv-scan.conf` (`XDG_CONFIG_HOME` defaults to `~/.config`)
  - on MacOS: `~/Library/Application Support/arxiv-scan/arxiv-scan.conf`
  - on Windows: `$HOME/Documents/arxiv-scan/arxiv-scan.conf`

# Feedback
All feedback, including bug reports, feature requests, pull requests, etc., is welcome. `arxiv-scan` is being actively developed in an open repository; if you have any trouble please raise an [issue](https://github.com/matiscke/arxiv-scan/issues/new).

---------------------
License: [MIT License](https://choosealicense.com/licenses/mit/)
