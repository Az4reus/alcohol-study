import sqlite3 as sq


def init_db() -> sq.Connection:
    c = sq.connect('./alcohol_study.db')
    cur = c.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS pictures (
      name TEXT,
      link BLOB,
      evaluated BOOLEAN,
      username TEXT
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
      answer_1 BLOB,
      answer_2 BLOB,
      answer_3 BLOB
    );
    """)
    c.commit()
    return c


def get_next_picture():
    c = init_db()
    cur = c.cursor()

    cur.execute("""
    SELECT name FROM pictures WHERE evaluated = 0 AND name != '' LIMIT 1;
    """)

    return cur.fetchall()[0][0]


def insert_picture(c: sq.Connection,
                   name: str,
                   link: str,
                   username: str,
                   evaluated: bool = 0):
    cursor = c.cursor()

    cursor.execute("INSERT INTO pictures VALUES (?, ?, ?, ?);",
                   [name,
                    link,
                    1 if evaluated else 0,
                    username])

    c.commit()


def count_unevaluated_pictures():
    conn = init_db()
    c = conn.cursor()

    return c.execute(
            "SELECT count(*) FROM pictures WHERE evaluated = 0 AND name != ''") \
        .fetchall()[0][0]


def insert_picture_data(form):
    shows_people = form['visible_people']
    picture_name = form['picture_name']
    focused_people = form['amount_focused_people']
    unfocued_people = form['amount_unfocused_people']


def get_user_ids():
    conn = init_db()
    c = conn.cursor()

    raw_data = c.execute("SELECT DISTINCT username FROM pictures").fetchall()
    return [t[0] for t in raw_data]
