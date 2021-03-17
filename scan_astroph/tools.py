"""Miscellaneous function which don't fit in other modules"""

import html
from urllib.request import urlopen


def load_html(address: str) -> str:
    ''' Load content from website

    Load HTML from address and convert HTML escape sequences to Unicode character
    '''
    with urlopen(address) as response:
        return html.unescape(response.read().decode())
