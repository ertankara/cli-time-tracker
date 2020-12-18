from datetime import datetime
from sqlite3 import Cursor
from helper import section_title, time_to_minutes
from db import provide_cursor


class Action:
    def __init__(self, fn, description, requires_flag=False):
        self.fn = fn
        self.description = description
        self.requires_flag = requires_flag


flags = {
    '--help': 'help',
    '-h': 'help',
    '--time': 'add_time',
    '-t': 'add_time',
    '-i': 'init_db',
    '--init': 'init_db',
    '--drop': 'drop_db',
    '-p': 'new_project',
    '--project': 'new_project',
    '--list': 'list_projects',
    '-l': 'list_projects'
}

flag_keys = flags.keys()


def get_corresponding_flag_action(raw_flag: str):
    parsed_flag = raw_flag.split('=')[0]
    if parsed_flag in flag_keys:
        target_action = flags_to_actions[flags[parsed_flag]]
        if target_action.requires_flag:
            target_action.fn(raw_flag)
        else:
            target_action.fn()
    else:
        print(f'Unknown flag was received {parsed_flag}')


def display_help_msg(_):
    print('Helper flag recieved')


def get_project_by_id(cursor: Cursor, project_id: int):
    cursor.execute('SELECT id, name FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    return project


def get_project_by_name(cursor: Cursor, project_name: str):
    cursor.execute(
        'SELECT id, name FROM projects WHERE name = ?', (project_name,))
    project = cursor.fetchone()
    return project


@provide_cursor
def register_time(cursor: Cursor, given_flag: str):
    err = False

    try:
        flag_value = given_flag.split('=')[1]
        time, project_name = flag_value.split('@')
        is_id = True
        project = None
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            project_name = int(project_name)
        except:
            is_id = False

        minutes_to_register = time_to_minutes(time)

        if minutes_to_register == None:
            raise ValueError('Time format is not in specified format')

        project = get_project_by_id(cursor,
                                    project_name) if is_id else get_project_by_name(cursor, project_name)

        if project == None:
            print('Project does not exist creating it first...')
            cursor.execute(
                'INSERT INTO projects (name) VALUES (?)', (project_name,))

            cursor.execute(
                'SELECT id, name FROM projects WHERE name = ?', (project_name,))

            project = get_project_by_name(cursor, project_name)

            cursor.execute('''INSERT INTO work_sessions (
                minutes,
                date,
                project_id
            ) VALUES (
                ?, ?, ?
            )
            ''', (minutes_to_register, current_date, project['id']))
        else:
            cursor.execute('''INSERT INTO work_sessions (
                minutes,
                date,
                project_id
            ) VALUES (
                ?, ?, ?
            )
            ''', (minutes_to_register, current_date, project['id']))
    except Exception as e:
        print('An error occurred while registering time', e)
        err = True

    return err


@provide_cursor
def init_db(cursor: Cursor):
    err = False
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                minutes INTEGER NOT NULL,
                date TEXT,
                project_id INTEGER REFERENCES projects (id)
            );
        ''')
    except:
        err = True

    return err


@provide_cursor
def drop_db(cursor: Cursor):
    err = False
    try:
        cursor.execute('''
            DROP TABLE IF EXISTS projects
        ''')
        cursor.execute('''
            DROP TABLE IF EXISTS work_sessions
        ''')
    except:
        err = True

    return err


@provide_cursor
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


@provide_cursor
def list_projects(cursor: Cursor):
    err = False
    try:
        cursor.execute('SELECT id, name FROM projects')
        projects = cursor.fetchall()

        section_title('Projects')
        for idx, p in enumerate(projects):
            print(f"{idx + 1} - ({p['id']}) {p['name']}")
    except:
        err = True

    return err


flags_to_actions = {
    'add_time': Action(register_time, 'Registers time as "worked hour"', True),
    'drop_db': Action(drop_db, '__DANGEROUS__ Drops worked hour records and projects not undoable'),
    'init_db': Action(init_db, 'Creates necessary tables, has no effect if tables are created previously'),
    'help': Action(display_help_msg, 'Display available helper methods'),
    'list_projects': Action(list_projects, 'Lists existing projects'),
    'new_project': Action(new_project, 'Creates a new project', True),
}
