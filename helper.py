def dict_factory(cursor, row):
    d = {}

    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]

    return d


def section_title(title: str):
    print(title)
    print('-' * len(title) + '-')
