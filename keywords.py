import json

def read_keywords(filename='keywords.txt'):
    with open(filename) as json_file:
        keywords = json.load(json_file)
    return keywords

TITLE_KEYWORDS = read_keywords()
AUTHORS = read_keywords('authors.txt')
