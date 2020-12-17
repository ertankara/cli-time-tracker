import sqlite3
from helper import dict_factory

connection = sqlite3.connect('./db.sqlite')
connection.row_factory = dict_factory


def close_connection():
    connection.close()
