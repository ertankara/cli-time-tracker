import db


class Action:
    def __init__(self, fn, description):
        self.fn = fn
        self.description = description


flags = {
    '--help': 'help',
    '-h': 'help',
    '--time': 'add_time',
    '-t': 'add_time',
    '-i': 'init_db',
    '--init': 'init_db',
    '--drop': 'drop_db'
}

flag_keys = flags.keys()


def get_corresponding_flag_action(raw_flag: str):
    parsed_flag = raw_flag.split('=')[0]
    if parsed_flag in flag_keys:
        target_flag_action = flags[parsed_flag]
        flags_to_actions[target_flag_action].fn(raw_flag)
    else:
        print(f'Unknown flag was received {parsed_flag}')


def display_help_msg(_):
    print('Helper flag recieved')


@db.provide_cursor
def register_time(cursor, given_flag):
    err = False

    try:
        pass
    except:
        err = True

    return err


@db.provide_cursor
def init_db(cursor, _):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount INTEGER NOT NULL,
            date TEXT
            project_id REFERENCES projects (id)
        );
    ''')


@db.provide_cursor
def drop_db(cursor, _):
    cursor.execute('''
        DROP TABLE IF EXISTS projects
    ''')
    cursor.execute('''
        DROP TABLE IF EXISTS hours
    ''')


flags_to_actions = {
    'help': Action(display_help_msg, 'Display available helper methods'),
    'add_time': Action(register_time, 'Registers time as "worked hour"'),
    'init_db': Action(init_db, 'Creates necessary models to track work'),
    'drop_db': Action(drop_db, '__DANGEROUS__ Drops worked hour records not undoable')
}
