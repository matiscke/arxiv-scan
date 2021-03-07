scan_astro-ph
=============
Scan abstract listings on ArXiV's astro-ph (or others) for keywords and favorite authors to distill a list of papers most relevant for *you*.
Keywords can be typed in manually or be found by ranking word occurrences in a provided file (e.g., a `.bib` file).

The bulk of the code was created by [Robert Glas](https://github.com/rmglas).

# Installation
Requirements: Python >3.5

These scripts can be installed with pip:
```
pip install --upgrade git+https://github.com/matiscke/scan_astro-ph.git#egg=scan_astroph
```
Depending on your Python installation, you might need one of the following:
```
pip3 install --upgrade git+https://github.com/matiscke/scan_astro-ph.git#egg=scan_astroph
python3 -m pip install --upgrade git+https://github.com/matiscke/scan_astro-ph.git#egg=scan_astroph
```

# Usage

## Set up keywords and relevant authors
### either manually:
- In your current working directory, create the files `authors.txt` and `keywords.txt`.
- write down your favorite authors and keywords, plus a ranking for each. I suggest integers ranging from 1 to 5, where 5 is most relevant. The *syntax* is just like for a *python dictionary*.

Example `authors.txt`:
```
{"Alpher" : 1, "Bethe" : 2, "Gamov" : 3}
```
Example `keywords.txt`:
```
{"star": 1, "planet": 2, "habitable": 3}
```

### or let `scan_astro-ph` do it for you:
- Run `scan_astro-ph.wordcounter` (or `python -m scan_astroph.wordcounter`).
It will ask for an ASCII file and extract words with 4-12 characters from it, sorted by occurrence in the file.
- You will be asked to rank these suggested keywords. For each word shown, press 'Enter' to reject it or provide an integer rating, e.g., from 1 to 5 (higher=more relevant). Conclude by pressing `C`.
- Manually insert particularly important authors and their ratings in `authors.txt` (currently, the automated search works only for keywords).


## Query today's astro-ph listing for relevant papers
Just run `scan_astro-ph` (or `python -m scan_astroph`).

## Options
```
'-d', '--date': date in format yyyy-mm, or "new", or "recent"', default=None
'-l', '--len': length of result list, all is -1, default=-1
'-v', '--rating': minimum rating for result list, default=6
'--reverse': reverse list (highest ranked paper on top), default=True
'--debug': debug mode, default=False
```

# Feedback
All feedback, including bug reports, feature requests, pull requests, etc., is welcome. `scan_astro-ph` is being actively developed in an open repository; if you have any trouble please raise an [issue](https://github.com/matiscke/scan_astro-ph/issues/new).

---------------------
License: [CC BY 3.0](http://creativecommons.org/licenses/by/3.0/)
