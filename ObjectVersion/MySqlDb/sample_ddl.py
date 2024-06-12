#!/usr/bin/env python

from __future__ import print_function
import mysql.connector

def open_db_conn(host="localhost", user="root", userpw="@Secret12", dbname=""):
  conn = mysql.connector.connect(
    host='127.0.0.1',
    user="root",
    password="@Secret12",
    database=dbname
  )
  print(f"opened {dbname}")
  return conn


def drop_db(dbname):
  sqlstr = f"DROP DATABASE {dbname}"
  db = open_db_conn()
  cur = db.cursor()
  cur.execute(sqlstr)
  print(f"{dbname} was dropped")
  db.close()


def create_db(dbname):
  sqlstr = f"CREATE DATABASE IF NOT EXISTS {dbname}"
  print(f"creating {dbname}")
  db = open_db_conn()
  cur = db.cursor()
  cur.execute(sqlstr)
  print(f"1 - {dbname} was created")
  #db.close()
  db = open_db_conn(dbname=dbname)
  print(f"2 - {dbname} was created")
  return db


def dbconnect(db_name):
  try:
    db = open_db_conn(dbname=db_name)
    print(f"connected to {db_name}")
  except mysql.connector.Error as err:
    if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
      print(f"database {db_name}, does not exist")
      db = create_db(db_name)
  print(db)
  return db


def create_tables(dbname):
  db = dbconnect(dbname)
  cursor = db.cursor()
  cursor.execute('''
  CREATE TABLE IF NOT EXISTS statements (
    id  INT NOT NULL AUTO_INCREMENT,
    action  VARCHAR(100),
    effect  VARCHAR(100),
    resource  VARCHAR(100),
    sid  VARCHAR(100),
    PRIMARY KEY (id)
  ) ENGINE=InnoDB
    ''')
  db.commit()

  

def old_create_tables():
  for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
      print(f"creating table {table_name}: ", end='')
      print()
    finally:
      print()


def main():
  dbname = "iam_db_4"
  db = dbconnect(dbname)
  print(db)
  #drop_db(dbname)
  create_tables(dbname)


if __name__ == '__main__':
  main()
