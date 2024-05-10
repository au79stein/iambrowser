#!/usr/bin/env python3

import sqlite3

def create_sqlite_in_memory():
    """ create a database connection to a database that resides
        in the memory
    """
    conn = None
    try:
        conn = sqlite3.connect(':memory:')
        print(sqlite3.sqlite_version)
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def create_sqlite_database(filename):
    """ create a database connection to an SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(filename)
        print(sqlite3.sqlite_version)
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


#FOREIGN KEY (inline_policy_id) REFERENCES policies (id)

def create_tables():
    sql_statements = [ 
        """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, 
                username text NOT NULL, 
                userid   text,
                arn      text NOT NULL,
                create_date TEXT, 
                pw_last_used_date TEXT
        );""",
        ]

    try:
        with sqlite3.connect('my.db') as conn:
            cursor = conn.cursor()
            for statement in sql_statements:
                cursor.execute(statement)
            
            conn.commit()
    except sqlite3.Error as e:
        print(e)


def add_user(conn, user):
    sql = '''INSERT INTO users(username,userid,arn,create_date,pw_last_used_date)
             VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, user)
    conn.commit()
    return cur.lastrowid


if __name__ == '__main__':
    create_sqlite_database("my.db")
    #create_sqlite_in_memory()
    create_tables()

    # 57: Username: rgoldstein, Arn: arn:aws:iam::079704269206:user/rgoldstein, Created: 04/25/2024 PasswordLastUsed: 05/09/2024
    try:
        with sqlite3.connect('my.db') as conn:
            # add a new user
            user = ('rgoldstein', '', 'arn:aws:iam::079704269206:user/rgoldstein', '04/25/2024', '05/09/2024')
            user_id = add_user(conn, user)
            print(f'Created a user with the id {user_id}')


    except sqlite3.Error as e:
        print(e)
