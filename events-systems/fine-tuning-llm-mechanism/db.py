import sqlite3

database = "answers.db"

create_table_answers = """
    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY,  
        content text,
        created_at DATE
    );
"""

create_table_feedbacks = """
    CREATE TABLE IF NOT EXISTS feedbacks (
        id INTEGER PRIMARY KEY,
        answer_id INTEGER,
        content text,
        rate INTEGER,
        created_at DATE,
        FOREIGN KEY (answer_id)
        REFERENCES answers (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    );
"""

try:
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute(create_table_answers)
        cursor.execute(create_table_feedbacks)
        conn.commit()
except sqlite3.OperationalError as e:
    print(e)