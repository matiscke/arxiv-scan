import json
import os.path
from collections import Counter
from re import findall

from . import keywords


def _count_words(fname):
    with open(fname) as f:
        text = f.read()
    words = findall(r'\b\w{4,12}\b', text.lower())
    return Counter(words)


def most_common_words_in_file(fname, n, verbose=False):
    counts = _count_words(fname)
    if verbose:
        for word, count in [['WORD', 'COUNT']] + counts.most_common(n):
            print(f'{word:>10} {count:>6}')
    return counts


def select_keywords(counts):
    """Let the user rate or reject keywords"""
    # sort list by decreasing number of occurrence
    counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))

    print('for each suggested keyword, give a rating from 1 to 5 or reject it by pressing "enter".\nConclude by pressing "C".')

    if os.path.exists('keywords.txt'):
        # don't ask for previously added words
        selected = keywords.read_keywords('keywords.txt')
        for key in selected:
            try:
                counts.pop(key)
            except KeyError:
                pass
    else:
        selected = {}

    for keyword in counts:
        while True:
            # repeat current iteration until a correct input was given
            usr_rating = input('{}: '.format(keyword))
            if (usr_rating == chr(27)) | (usr_rating.lower() == 'c'):
                # escape was pressed
                return selected
            elif usr_rating == "":
                break
            else:
                try:
                    selected[keyword] = int(usr_rating)
                    break
                except ValueError:
                    print('rating must be an integer.')
                    continue
    return selected

def selected2file(selected, filename='keywords.txt'):
    """write the selected keywords to a file."""
    with open(filename, 'w') as file:
        file.write(json.dumps(selected))


def main():
    les_mis_file = input('path to file: ')
    counts = most_common_words_in_file(les_mis_file, 200, verbose=False)
    selected = select_keywords(counts)
    selected2file(selected)

if __name__ == "__main__":
    main()
