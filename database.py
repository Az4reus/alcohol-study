import os
import sqlite3 as sq
import json

import time

import csv_reading


def init_db() -> sq.Connection:
    c = sq.connect('./alcohol_study.db')
    cur = c.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS pictures (
      name TEXT,
      link BLOB,
      evaluated BOOLEAN,
      username TEXT,
      obsolete BOOLEAN
    );

    CREATE TABLE IF NOT EXISTS picture_evaluation_data (
      picture_name TEXT,
      shows_people BOOLEAN,
      focused_people INTEGER,
      nonfocused_people INTEGER
    );

    CREATE TABLE IF NOT EXISTS picture_focal_result_data (
      picture_name TEXT NOT NULL,
      person_from_left INTEGER NOT NULL,
      answer_1 INTEGER,
      answer_1_text TEXT,
      answer_2 INTEGER,
      answer_3 INTEGER,
      answer_4 INTEGER,
      answer_5 INT,
      answer_6 INT,
      answer_7 INT,
      answer_8 INT,
      answer_9 INT,
      answer_10 INT,
      answer_11 INT,
      answer_12 INT
    );

    CREATE TABLE IF NOT EXISTS picture_non_focal_result_data (
      picture_name TEXT NOT NULL,
      answers BLOB
    );
    """)
    c.commit()
    return c


def get_next_picture():
    c = init_db()
    cur = c.cursor()

    cur.execute("""
    SELECT link, username FROM pictures
    WHERE evaluated = 0
    AND name != ''
    LIMIT 1;
    """)

    return cur.fetchall()[0]


def get_next_user_id_picture(id):
    c = init_db()
    cur = c.cursor()

    cur.execute('''
    SELECT link FROM pictures
    WHERE evaluated = 0
    AND name != ''
    AND pictures.username = ?
    LIMIT 1
    ''', [id])

    return cur.fetchall()


def insert_picture(c: sq.Connection,
                   name: str,
                   link: str,
                   username: str,
                   evaluated: bool = False,
                   obsolete: bool = False):
    cursor = c.cursor()

    try:
        _ = cursor.execute("SELECT * FROM pictures WHERE name=?",
                           [name]).fetchall()[0][0]

    except IndexError:

        cursor.execute("INSERT INTO pictures VALUES (?, ?, ?, ?, ?);",
                       [name,
                        link,
                        1 if evaluated else 0,
                        username,
                        1 if obsolete else 0])

    c.commit()


def count_unevaluated_pictures():
    conn = init_db()
    c = conn.cursor()

    return c.execute(
            "SELECT count(*) FROM pictures WHERE evaluated = 0 AND name != ''") \
        .fetchall()[0][0]


def insert_picture_data(form):
    shows_people = True if form['containsPeople'] == 'Yes' else False
    picture_name = form['picture_name']
    focused_people = form['focalSubjects']
    nonfocused_people = form['nonFocalSubjects']
    obsolete = 'isObsolete' in form

    c = init_db()
    cur = c.cursor()

    cur.execute("""
    INSERT INTO picture_evaluation_data VALUES (?, ?, ?, ?)
    """, [picture_name, shows_people, focused_people, nonfocused_people])

    c.commit()

    cur.execute("""
    UPDATE pictures SET evaluated = 1 WHERE link=?
    """, [picture_name])

    c.commit()

    if obsolete:
        cur.execute("UPDATE pictures SET obsolete = 1 WHERE name = ?",
                    [picture_name])
        c.commit()

    c.close()


def get_user_ids():
    conn = init_db()
    c = conn.cursor()

    raw_data = c.execute("SELECT DISTINCT username FROM pictures").fetchall()
    return [t[0] for t in raw_data]


def get_waiting_user_ids():
    conn = init_db()
    c = conn.cursor()

    raw_data = c.execute("""
    SELECT DISTINCT username
    FROM pictures INNER JOIN picture_evaluation_data
      ON pictures.link = picture_evaluation_data.picture_name
    WHERE
    pictures.evaluated = 1
    AND pictures.obsolete = 0
    AND picture_evaluation_data.shows_people = 1
    """).fetchall()

    return [t[0] for t in raw_data]


def get_relevant_pictures_for_user(user_id):
    conn = init_db()
    cur = conn.cursor()

    raw_data = cur.execute(
            """SELECT pictures.link
            FROM pictures INNER JOIN picture_evaluation_data
              ON pictures.link = picture_evaluation_data.picture_name
            WHERE pictures.username=?
            AND pictures.evaluated = 1
            AND picture_evaluation_data.shows_people = 1
            LIMIT 1""",
            [user_id]).fetchall()

    return raw_data[0][0]


def get_evaluation_data_for_picture(picture_file_name: str):
    conn = init_db()
    cur = conn.cursor()

    raw_data = cur.execute(
            "SELECT * FROM picture_evaluation_data WHERE picture_name = ?",
            [picture_file_name]).fetchall()[0]

    try:
        fp = int(raw_data[2])
    except ValueError:
        fp = 0

    try:
        ufp = int(raw_data[3])
    except ValueError:
        ufp = 0

    return fp, ufp


def upload_csv(files, app_config):
    csv_file = files['upload']
    filename = str(int(time.time())) + '.csv'
    csv_file.save(os.path.join(app_config, filename))

    csv_reading.read_data_csv(os.path.join(app_config, filename))


def _allowed_file_name(file_name):
    return file_name.rsplit('.', 1)[1] == 'csv'


def get_evaluations_left(picture_name):
    conn = init_db()
    cur = conn.cursor()

    left = cur.execute(
            '''SELECT count(*)
               FROM picture_focal_result_data
               WHERE picture_name = ?''',
            [picture_name]).fetchall()[0][0]

    focal_subjects = cur.execute(
            '''SELECT focused_people
               FROM picture_evaluation_data
               WHERE picture_name = ?''',
            [picture_name]).fetchall()[0][0]

    try:
        focal_subjects = int(focal_subjects)
    except ValueError:
        focal_subjects = 0

    return focal_subjects - left


def save_focal_survey_result(f):
    conn = init_db()
    cur = conn.cursor()

    picture_name = f['picture_name']
    person_from_left = cur.execute(
            """SELECT count(*)
               FROM picture_focal_result_data
               WHERE picture_name = ?""",
            [picture_name]).fetchall()[0][0] + 1

    q1 = f['q1']
    q1_text = ''
    if q1 == 'A family member' or q1 == 'other':
        q1_text = f['q1_textbox']

    q2 = f['q2']
    if q2 == '':
        q2 = 0

    q3 = f['q3']
    q4 = f['q4']
    q5 = f['q5']
    q6 = f['q6']
    q7 = f['q7']
    q8 = f['q8']
    q9 = f['q9']
    q10 = f['q10']
    q11 = f['q11']
    q12 = f['q12']

    cur.execute("""
    INSERT INTO picture_focal_result_data VALUES (?, ?, ?, ?, ?,
     ?, ?, ?, ?, ?,
     ?, ?, ?, ?, ?)
  """, [picture_name, person_from_left, q1, q1_text, q2, q3, q4, q5, q6, q7, q8,
        q9, q10, q11, q12])

    conn.commit()


def save_nf_survey_result(f, unfocused_people):
    conn = init_db()
    cur = conn.cursor()

    dict = f.to_dict()
    dict['unfocusedPeople'] = unfocused_people
    picture = dict['picture_name']

    j = json.dumps(dict)

    cur.execute('''
    INSERT INTO picture_non_focal_result_data VALUES (?, ?)
    ''', [picture, j])

    conn.commit()


def drop_database():
    os.remove('./alcohol_study.db')
    init_db()


def has_nf_data(picture):
    c = init_db()
    cur = c.cursor()

    isempty = cur.execute('''
    SELECT * FROM picture_non_focal_result_data WHERE picture_name = ?
    ''', [picture]).fetchall()

    return isempty != []
