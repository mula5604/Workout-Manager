import sqlite3

class Database:
    def __init__(self, path="workout_tracker.db"):
        self.conn = sqlite3.connect(path)
             

    def execute(self, query, params=()): #makes the whole cursor and execute sequence easier to work with
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    