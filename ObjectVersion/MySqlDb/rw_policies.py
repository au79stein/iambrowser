#!/usr/bin/env python

#from __future__ import print_function
import mysql.connector
import json


def read_policy(pname):
  #test_file = f"../Output/terraform-staging-only"
  test_file = f"../Output/AllowMFAmanagement"
  f = open(test_file, 'r')
  data = json.load(f)
  for i in data['Statement']:
    if 'Sid' in i:
      print(f"""{pname},{i['Effect']},{i['Sid']},{i['Resource']},<<<{i['Action']}>>>""")
    else:
      print(f"""{pname},{i['Effect']},no-sid,{i['Resource']},<<<{i['Action']}>>>""")
  f.close()


def test_rw_policies(dbname):
  read_policy('test')


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
  db.close()

  

def main():
  dbname = "iam_db_4"
  db = dbconnect(dbname)
  print(db)
  #drop_db(dbname)
  create_tables(dbname)
  test_rw_policies(dbname)


if __name__ == '__main__':
  main()
