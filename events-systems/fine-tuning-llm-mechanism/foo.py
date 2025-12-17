import sqlite3


database = "answers.db"

if __name__ == "__main__":
    with sqlite3.connect(database) as client:
        cursor = client.cursor()
        res = cursor.execute("delete from  answers")
        print(res.fetchall())
