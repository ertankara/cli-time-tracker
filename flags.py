import db
from helper import section_title
from sqlite3 import Cursor


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
    '--drop': 'drop_db',
    '--p': 'new_project',
    '--project': 'new_project',
    '--list': 'list_projects',
    '-l': 'list_projects'
}

flag_keys = flags.keys()


def get_corresponding_flag_action(raw_flag: str):
    parsed_flag = raw_flag.split('=')[0]
    if parsed_flag in flag_keys:
        target_action = flags_to_actions[flags[parsed_flag]]
        target_action.fn(raw_flag)
    else:
        print(f'Unknown flag was received {parsed_flag}')


def display_help_msg(_):
    print('Helper flag recieved')


@db.provide_cursor
def register_time(cursor: Cursor, given_flag: str):
    err = False

    try:
        raw_time, project_name = given_flag.split('@')
        time = raw_time.split('=')[1]

        cursor.execute('''

        ''')
    except:
        err = True

    return err


@db.provide_cursor
def init_db(cursor: Cursor, _):
    err = False
    try:
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
    except:
        err = True

    return err


@db.provide_cursor
def drop_db(cursor: Cursor, _):
    err = False
    try:
        cursor.execute('''
            DROP TABLE IF EXISTS projects
        ''')
        cursor.execute('''
            DROP TABLE IF EXISTS hours
        ''')
    except:
        err = True

    return err


@db.provide_cursor
def new_project(cursor: Cursor, given_flag: str):
    err = False
    try:
        project_name = given_flag.split('=')[1]

        cursor.execute('''
            INSERT INTO projects (name) VALUES (?)
        ''', (project_name,))

        print(f'{project_name} created successfully!')
    except:
        err = True

    return err


@db.provide_cursor
def list_projects(cursor: Cursor, _):
    err = False
    try:
        cursor.execute('SELECT name FROM projects')
        projects = cursor.fetchall()

        section_title('Projects')
        for idx, p in enumerate(projects):
            print(f"{idx + 1} - {p['name']}")
    except:
        err = True

    return err


flags_to_actions = {
    'add_time': Action(register_time, 'Registers time as "worked hour"'),
    'drop_db': Action(drop_db, '__DANGEROUS__ Drops worked hour records and projects not undoable'),
    'init_db': Action(init_db, 'Creates necessary tables, has no effect if tables are created previously'),
    'help': Action(display_help_msg, 'Display available helper methods'),
    'list_projects': Action(list_projects, 'Lists existing projects'),
    'new_project': Action(new_project, 'Creates a new project'),
}
