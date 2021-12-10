"""Read configuration files"""

import json
import os
import subprocess
import sys
from ast import literal_eval
from configparser import ConfigParser
from pathlib import Path


class Config:
    """configparser.ConfigParser wrapper with type conversion

    Internally stores the configuration in a configparser.Configparser object,
    but adds method for accessing keywords and authors with the right types, as
    configparser only uses `str`
    """

    def __init__(self):
        self._config = ConfigParser()

        self._config["keywords"] = {}
        self._config["authors"] = {}
        self._config["options"] = {
            "categories": "astro-ph.EP",
            "date": "new",
            "length": -1,
            "minimum_rating": 10,
            "reverse_list": False,
            "show_resubmissions": False,
            "show_cross_lists": True,
        }

    @property
    def keywords(self) -> dict:
        """Get keywords/rating as dict with type `dict[str,int]`"""
        return {
            keyword: int(rating) for keyword, rating in self._config["keywords"].items()
        }

    def add_keyword(self, keyword: str, rating: int):
        """Add keyword with rating to config"""
        self._config["keywords"][keyword] = str(rating)

    @property
    def authors(self):
        """Get authors/rating as dict with type `dict[str,int]`"""
        return {
            author: int(rating) for author, rating in self._config["authors"].items()
        }

    def add_author(self, author: str, rating: int):
        """Add author with rating to config"""
        self._config["authors"][author] = str(rating)

    def read(self, path: Path):
        """Read path to config. Existing values will be overwritten"""
        self._config.read(path)

    def write(self, path: Path, overwrite: bool = False):
        """Write config to file. Will not overwrite existing files if `overwrite` is false"""
        with open(path, "w" if overwrite else "x") as f:
            self._config.write(f)

    def __getitem__(self, key: str):
        """Get option value from config"""
        # use literal_eval to convert if its not a str
        try:
            return literal_eval(self._config["options"][key])
        except (ValueError, SyntaxError):
            return self._config["options"][key]

    def __setitem__(self, key, value):
        """Set option if value is not None"""
        if value is not None:
            self._config["options"][key] = str(value)


def find_configfile() -> Path:
    """Finds location of configuration file"""
    # Check environment variable
    if "ARXIV_SCAN_CONF" in os.environ:
        return Path(os.path.expandvars(os.environ["ARXIV_SCAN_CONF"]))

    # check home directory
    configpath = Path.home() / ".arxiv-scan.conf"
    if configpath.is_file():
        return configpath

    # check platform specific configuration location
    configpath = configfile_default_location()
    if configpath.is_file():
        return configpath

    raise FileNotFoundError("Could not find arxiv-scan.conf. Check Readme for config locations")

def configfile_default_location(mkdir: bool=False) -> Path:
    """Find platform dependent configfile location

    With `mkdir=True` all parent directories for the config file are created.

    On Linux: `$XDG_CONFIG_HOME/arxiv-scan/arxiv-scan.conf` (`~/.config/arxiv-scan/arxiv-scan.conf`)
    On Windows: `$HOME/Documents/arxiv-scan/arxiv-scan.conf`
    On MacOS: `$HOME/Library/Application Support/arxiv-scan/arxiv-scan.conf`

    For more details check out documentation of appdirs
    """
    if sys.platform == "darwin": # MacOS
        path = Path.home() / "Library" / "Application Support" / "arxiv-scan" / "arxiv-scan.conf"
    elif sys.platform == "win32": # Windows
        path = Path.home() / "Documents" / "arxiv-scan" / "arxiv-scan.conf"
    else: # Linux and other Unixes
        path = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "arxiv-scan" / "arxiv-scan.conf"

    if mkdir:
        path.parent.mkdir(parents=True, exist_ok=True)

    return path


def file_editor(path: Path):
    """Open file in default text editor

    Opens in first editor set in environment variables $VISUAL or $EDITOR,
    otherwise defaults to `vi` on unixes and Notepad on Windows.
    """
    if "VISUAL" in os.environ:
        subprocess.run((os.environ["VISUAL"], path))
    elif "EDITOR" in os.environ:
        subprocess.run((os.environ["EDITOR"], path))
    elif sys.platform == "win32":
        subprocess.run(["notepad.exe", path])
    else:
        subprocess.run(("vi", path))

def load_config_legacy_format(keywords_path: Path, authors_path: Path) -> Config:
    """Load config from legacy format (seperate JSON files for keywords and authors"""
    config = Config()

    with open(keywords_path) as f:
        keywords = json.load(f)
    for keyword, rating in keywords.items():
        config.add_keyword(keyword, rating)

    with open(authors_path) as f:
        authors = json.load(f)
    for author, rating in authors.items():
        config.add_author(author, rating)

    return config
