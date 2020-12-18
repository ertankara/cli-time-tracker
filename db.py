from os import path
import sqlite3
from helper import dict_factory

dir_parts = path.abspath(__file__).split('/')
db_dir = '/'.join(dir_parts[:-1])

connection = sqlite3.connect(db_dir + '/db.sqlite')
connection.row_factory = dict_factory


def close_connection():
    connection.close()


def provide_cursor(fn):
    cursor = connection.cursor()

    def wrapper(*args, **kwargs):
        err = fn(cursor, *args, **kwargs)
        if err:
            connection.rollback()
            cursor.close()
            return

        connection.commit()
        cursor.close()

    return wrapper
