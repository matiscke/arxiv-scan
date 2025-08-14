import urllib
import urllib.request
import time

from xml.etree import ElementTree

from .oai_api import namespaces, base_url, attempts


def check_categories(categories):
    """Check if given arXiv categories exist

    If one of the categories does not exist, we print all available categories
    and raise ValueError.

    Note that we obtain the recent arXiv categories with a (rather fast) server
    request via the OAI API.

    Args:
        categories (list): List of arXiv subjects (e.g. `physics:astro-ph:EP`)
    """
    url = f"{base_url:s}?verb=ListSets"

    # get data from server
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

    # parse XML data
    root = tree.getroot()
    xml_categories = root.findall("./oai:ListSets/oai:set", namespaces=namespaces)

    # retrieve categories from XML data
    categories_all = []
    for cat in xml_categories:
        categories_all.append(cat.find("./oai:setSpec", namespaces=namespaces).text)
    categories_all.sort()

    # check if categories are found
    not_found = []
    for cat in categories:
        if cat not in categories_all:
            not_found.append(cat)

    # print available categories in case one or more were not found
    if len(not_found) > 0:
        print("\nAvailable categories:")
        groups = set([cat.split(":")[0] for cat in categories_all])
        for group in groups:
            print(group)
            group_cat = []
            for cat in categories_all:
                if cat.startswith(group) and cat != group:
                    group_cat.append(cat)
            print(", ".join(group_cat))
        print()
        for cat in not_found:
            print(f"Category not found: {cat:s}")
        raise ValueError(f"Category not found")
