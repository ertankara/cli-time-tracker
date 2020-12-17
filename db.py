import sqlite3
from helper import dict_factory

connection = sqlite3.connect('./db.sqlite')
connection.row_factory = dict_factory


def close_connection():
    connection.close()


def provide_cursor(fn):
    cursor = connection.cursor()

    def wrapper(*args, **kwargs):
        err = fn(cursor, *args, **kwargs)
        if err:
            print('execs this line', err)
            connection.rollback()
            cursor.close()
            return

        connection.commit()
        cursor.close()

    return wrapper
