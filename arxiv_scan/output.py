"""Functions related to outputting to terminal"""
from termcolor import colored

def print_entries(entries: list):
    ''' Print all entries'''
    for i, entry in enumerate(entries):
        rating = colored('({:2d})'.format(entry.rating), 'green')
        authors = []
        authors_len = 0
        for i, a in enumerate(entry.authors):
            if authors_len + len(a) > 90:
                authors.append(colored('...', attrs=['underline']))
                break
            authors_len += len(a)
            if entry.author_marks[i]:
                authors.append(colored(a, 'red', attrs=['underline']))
            else:
                authors.append(colored(a, attrs=['underline']))
        authors = colored(', ', attrs=['underline']).join(authors)

        title_lines = [[]]
        title_len = 0
        for i, t in enumerate(entry.title):
            if t == ' ' and title_len > 90:
                title_len = 0
                title_lines.append([])
                continue
            title_len += 1
            if i in entry.title_marks:
                title_lines[-1].append(colored(t, 'blue'))
            else:
                title_lines[-1].append(t)
        title_lines = [''.join(t) for t in title_lines]

        print('{rating:s} {arxiv:s}{id:s}'.format(
            rating=rating,
            arxiv=colored('https://arxiv.org/abs/', 'green'),
            id=colored(entry.id, 'green')))
        print('     {authors:s}'.format(authors=authors))
        for line in title_lines:
            print('     {title:s}'.format(title=line))

        print(f"     submitted {entry.date_submitted} on {entry.category}")
