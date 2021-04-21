"""Read configuration files"""

import json
import os
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
            "date": "new",
            "length": -1,
            "minimum_rating": 6,
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
        except ValueError:
            return self._config["options"][key]

    def __setitem__(self, key, value):
        """Set option if value is not None"""
        if value is not None:
            self._config["options"][key] = str(value)


def find_configfile():
    """Finds location of configuration file"""
    # Check environment variable
    if "SCAN_ASTRO_PH_CONF" in os.environ:
        return Path(os.path.expandvars(os.environ["SCAN_ASTRO_PH_CONF"]))

    # check home directory
    configpath = Path.home() / ".scan_astro-ph.conf"
    if configpath.is_file():
        return configpath

    # CHECK $XDG_CONFIG_HOME
    if "XDG_CONFIG_HOME" in os.environ:
        configpath = Path(os.environ["XDG_CONFIG_HOME"]) / "scan_astro-ph.conf"
    else:
        configpath = Path.home() / ".config" / "scan_astro-ph.conf"
    if configpath.is_file():
        return configpath
    else:
        raise FileNotFoundError("Cannot find configuration file")


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
