import sqlite3

class Database:
    def __init__(self, path="workouts.db"):
        self.conn = sqlite3.connect(path)

    def execute(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    