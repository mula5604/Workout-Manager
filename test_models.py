import pytest
from models import *


# db
test_db = Database(path="test_workout_tracker.db")


# tests for split table
test_split = Split(db=test_db,name="upper")

def test_split_save():
    #tests if saving works
    test_db.execute(query="DELETE FROM splits;")
    test_split.save()
    assert test_db.fetchall("SELECT name FROM splits") == [("upper",)]

def test_get_by_name():
    #tests if getting by name works
    temp = Split.get_by_name(test_db,"upper")
    assert temp.name == "upper"

def test_get_workout():
    temp = test_split.get_workouts()
    assert temp != 1

def test_delete():
    test_split.delete()
    assert test_split.name not in test_db.fetchall("SELECT name FROM splits")