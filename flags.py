from datetime import datetime
from sqlite3 import Cursor
from helper import section_title, time_to_minutes, minutes_to_time
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
    '-l': 'list_projects',
    '-r': 'read_report',
    '--report': 'read_report',
    '-set-goal': 'set_goal',
    '-s': 'set_goal'
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


def display_help_msg():
    global flags
    actions = {}

    for cli_flag, action in flags.items():
        if actions.get(action, None) is None:
            actions[action] = cli_flag
        else:
            actions[action] = f'{cli_flag}, {actions.get(action)}'

    max_len = max(map(lambda x: len(x), actions.values()))

    for action, flags in actions.items():
        spaces = (max_len - len(flags)) * ' '
        print(f'{flags} {spaces} {flags_to_actions[action].description}')


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
        print('An error occurred while registering time, check --help', e)
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

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_goal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal INTEGER
            );
        ''')

        # 400 minutes daily goal by default
        # 6h 40m, we mean business!
        cursor.execute('INSERT INTO daily_goal (goal) VALUES (?)', (400,))
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


@provide_cursor
def set_goal(cursor: Cursor, given_flag: str):
    err = False

    try:
        new_goal = int(given_flag.split('=')[1])
        cursor.execute('''
            UPDATE daily_goal SET goal = ?
        ''', (new_goal,))

        print(f'New daily goal is set to {new_goal}')
    except:
        err = True

    return err


def get_daily_report(cursor: Cursor):
    cursor.execute('''
        SELECT
            (SELECT goal FROM daily_goal) AS daily_goal,
            (
                SELECT SUM(ws.minutes)
                FROM work_sessions AS ws
                WHERE strftime('%Y-%m-%d', date('now')) = strftime('%Y-%m-%d', ws.date)
            ) AS todays_total

    ''')

    stats = cursor.fetchone()

    cursor.execute('''
        SELECT AVG(daily_sum.daily_total) AS daily_average
        FROM (
            SELECT SUM(ws.minutes) AS daily_total, strftime('%Y-%m-%d', ws.date) AS day
            FROM work_sessions ws
            GROUP BY 2
        ) AS daily_sum
    ''')

    day_avg = cursor.fetchone()
    daily_goal = minutes_to_time(stats['daily_goal'])
    todays_total = minutes_to_time(stats['todays_total'])
    remaining_time_until_goal = stats['daily_goal'] - stats['todays_total']

    congrats = 'Goal reached, take a break... Or set a new goal with -s flag you challenger!'
    remaining = f'Until goal is reached: {minutes_to_time(remaining_time_until_goal)}'

    formatted_remaining_time = remaining if remaining_time_until_goal > 0 else congrats

    section_title(f'Daily (avg: {day_avg["daily_average"]})')

    if todays_total is None:
        print(f'Daily goal: {daily_goal}')
        print('No work was done today')

    print(f'Daily goal: {daily_goal}')
    print(f'Todays total: {todays_total}')
    print(formatted_remaining_time)


def get_monthly_report(cursor: Cursor):
    print('Monthly')


def get_yearly_report(cursor: Cursor):
    print('Yearly report')


@provide_cursor
def read_report(cursor: Cursor, given_flag: str):
    parsed_flag = given_flag.split('=')
    flag_value = parsed_flag[1] if len(parsed_flag) > 1 else 'd'

    if flag_value == 'd':
        get_daily_report(cursor)
    elif flag_value == 'm':
        get_monthly_report(cursor)
    elif flag_value == 'y':
        get_yearly_report(cursor)


flags_to_actions = {
    'add_time': Action(register_time, 'Registers time as "worked hour"', True),
    'drop_db': Action(drop_db, '__DANGEROUS__ Drops worked hour records and projects not undoable'),
    'init_db': Action(init_db, 'Creates necessary tables, has no effect if tables are created previously'),
    'help': Action(display_help_msg, 'Display available helper methods'),
    'list_projects': Action(list_projects, 'Lists existing projects'),
    'new_project': Action(new_project, 'Creates a new project', True),
    'read_report': Action(read_report, 'Reads reports with various intervals based on specified flag', True),
    'set_goal': Action(set_goal, 'Set daily goal for yourself 6h 40m by default', True)
}
