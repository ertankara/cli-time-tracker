def dict_factory(cursor, row):
    d = {}

    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]

    return d


def section_title(title: str):
    print(title)
    print('-' * len(title) + '-')


def time_to_minutes(t: str):
    lower_t = t.lower()
    total_minutes = 0
    try:
        if lower_t.find('h') != -1:
            hours, minutes = lower_t.split('h')
            total_minutes += int(hours) * 60

            if minutes:
                if minutes.find('m') != -1:
                    total_minutes += int(minutes.split('m')[0])
                else:
                    total_minutes += int(minutes)
        else:
            if lower_t.find('m') != -1:
                minutes = lower_t.split('m')
                total_minutes += int(minutes.split('m')[0])
            else:
                total_minutes += int(lower_t)

        return total_minutes
    except:
        return None


def minutes_to_time(m: int):
    hours = m // 60
    minutes = m % 60

    output = ''

    if hours > 0:
        output += f'{hours}h'

    if minutes > 0:
        output += f'{minutes}m'

    # 0m if hours are 0 as well
    return output if len(output) > 0 else '0m'
