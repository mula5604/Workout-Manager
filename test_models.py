# NEED TO MAKE BETTER TEST DB
# NEED TO MAKE TESTS HERE LESS REPETETIVE
# THIS IS A TO DO
#
#



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

def test_get_by_name_splits():
    #tests if getting by name works
    temp = Split.get_by_name(test_db,"upper")
    assert temp.name == "upper"

def test_get_workout_splits():
    #NEED TO MAKE WORKOUTS TO WORK
    temp = test_split.get_workouts()
    assert temp != 1

def test_delete_splits():
    test_split.delete()
    assert test_split.name not in test_db.fetchall("SELECT name FROM splits")

# tests for excercise table
test_excercise = Exercise(test_db,"bench press")

def test_excercise_save():
    test_db.execute(query="DELETE FROM exercises;")
    test_excercise.save()
    assert test_db.fetchall("select name from exercises;") == [("bench press",)]

def test_get_by_name_excercises():
    temp = Exercise.get_by_name(test_db,"bench press")
    assert temp.name == "bench press"

def test_get_logs_excercises():
    #need to make excercise logs first
    pass

def test_delete_excercises():
    test_excercise.delete()
    assert test_excercise.name not in test_db.fetchall("select name from exercises;")

# tests for workout table

test_workout = Workout(test_db, test_split.id, "upper workout")

def test_workout_save():
    # tests if saving works
    pass


def test_get_by_name_workout():
    # tests if getting by name works
    #need to make a better test db
    pass


def test_get_exercises_workout():
    # need to make workout exercises first
    pass


def test_get_logs_workout():
    # need to make workout logs first
    pass

def test_delete_workout():
    # tests if deleting works

    test_workout.delete()

    assert test_workout.name not in test_db.fetchall("SELECT name FROM workouts")