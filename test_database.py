import pytest
from database import *

def test_execute_tables():
    db = Database()
    result = db.execute(query="SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
    assert result.fetchall() == [('splits',), ('exercises',), ('workouts',), ('workout_exercises',), ('workout_logs',), ('exercise_logs',)]


def test_execute_insert():
    db = Database()
    db.execute(query="DELETE FROM splits;")
    insert_q = db.execute(query="INSERT INTO splits (name) VALUES (?)",params=("upper",))
    result = db.execute(query="SELECT name from splits")
    assert "upper" in result.fetchall()[0]
