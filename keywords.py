import json

def read_keywords(filename='keywords.txt'):
    with open(filename) as json_file:
        keywords = json.load(json_file)
    return keywords

TITLE_KEYWORDS = read_keywords()

AUTHORS = {
    'Mordasini':5,
    'Alibert' : 5,
    'Espinoza' : 5
}
