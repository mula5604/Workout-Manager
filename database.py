import sqlite3

class Database:

    def __init__(self, path="workout_tracker.db"):
        self.conn = sqlite3.connect(path)

    def execute(self, query, params=()):  # makes the whole cursor and execute sequence easier to work with
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    def get_id_or_raise(self, table, column, value, error_message):
        result = self.execute(
            f"SELECT id FROM {table} WHERE {column} = ?",
            (value,)
        ).fetchone()

        if result:
            return result[0]

        raise ValueError(error_message)

    def insert(self, query, params=()):
        cursor = self.execute(query, params)
        return cursor.lastrowid

    def delete(self, query, params=()):
        self.execute(query, params)

    def fetchone(self, query, params=()):
        return self.execute(query, params).fetchone()

    def fetchall(self, query, params=()):
        return self.execute(query, params).fetchall()