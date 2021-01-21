from collections import Counter
from re import findall


def _count_words(fname):
    with open(fname) as f:
        text = f.read()
    words = findall(r'\b\w{5,6}\b', text.lower())
    return Counter(words)


def most_common_words_in_file(fname, n):
    counts = _count_words(fname)
    for word, count in [['WORD', 'COUNT']] + counts.most_common(n):
        print(f'{word:>10} {count:>6}')


if __name__ == "__main__":
    les_mis_file = input('path to file: ')
    most_common_words_in_file(les_mis_file, 50)