import pytest
from database import *

def test_execute_tables():
    #tests if the tables are being created
    db = Database()
    result = db.execute(query="SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
    assert result.fetchall() == [('splits',), ('exercises',), ('workouts',), ('workout_exercises',), ('workout_logs',), ('exercise_logs',)]


def test_execute_insert():
    #tests if regular queries work
    db = Database()
    db.execute(query="DELETE FROM splits;")
    db.execute(query="INSERT INTO splits (name) VALUES (?)",params=("upper",))
    result = db.execute(query="SELECT name from splits")
    assert "upper" in result.fetchall()[0]

def test_get_id_or_raise():
    #tests if correct things is being returned
    db = Database()
    db.execute(query="DELETE FROM splits;")
    split_id = db.insert("INSERT INTO splits (name) VALUES (?)", ("upper",))
    result = db.get_id_or_raise("splits", "name", "upper", "it aint there")
    assert result == split_id

def test_insert():
    #tests insert wrapper
    db = Database()
    db.execute(query="DELETE FROM splits;")
    db.insert("INSERT INTO splits (name) VALUES (?)", ("upper",))
    assert "upper" in db.execute(query="SELECT name from splits").fetchall()[0]

def test_delete():
    # tests delete wrapper
    db = Database()
    db.execute(query="DELETE FROM splits;")
    db.insert("INSERT INTO splits (name) VALUES (?)", ("upper",))
    db.delete("DELETE FROM splits WHERE name = ?", ("upper",))
    assert db.execute(query="SELECT name FROM splits").fetchall() == []

def test_fetchone():
    # tests fetchone wrapper
    db = Database()
    db.execute(query="DELETE FROM splits;")
    db.insert("INSERT INTO splits (name) VALUES (?)", ("upper",))
    assert db.fetchone("SELECT name FROM splits WHERE name = ?", ("upper",))[0] == "upper"

def test_fetchall():
    # tests fetchall wrapper
    db = Database()
    db.execute(query="DELETE FROM splits;")
    db.insert("INSERT INTO splits (name) VALUES (?)", ("upper",))
    db.insert("INSERT INTO splits (name) VALUES (?)", ("lower",))
    assert db.fetchall("SELECT name FROM splits") == [("upper",), ("lower",)]