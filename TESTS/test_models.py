# tests all functions for table the functions from models
# tests if the models save, retrieve, and delete data correctly

# TODO:
# reduce repetitive test setup



import pytest
from Workout_Manager.SRC.models import *


# db
test_db = Database(path="test_workout_tracker.db")


# split tests

def test_split_save():
    #tests if saving works
    test_db.execute(query="DELETE FROM splits;")
    test_split = Split(db=test_db,name="upper/lower")

    test_split.save()

    assert test_db.fetchall("SELECT name FROM splits") == [("upper/lower",)]

def test_get_by_name_splits():
    #tests if getting by name works
    test_db.execute(query="DELETE FROM splits;")
    test_split = Split(db=test_db,name="upper/lower")

    test_split.save()

    temp = Split.get_by_name(test_db,"upper/lower")
    assert temp.name == "upper/lower"

def test_get_workout_splits():
    test_db.execute(query="DELETE FROM splits;")
    test_db.execute(query="DELETE FROM workouts;")

    test_split = Split(db=test_db, name="upper/lower")
    test_split.save()

    temp_workout = Workout(test_db, test_split.id, "upper")
    temp_workout.save()

    splits_workouts = test_split.get_workouts()

    assert splits_workouts == [(temp_workout.id, "upper")]


def test_delete_splits():
    test_db.execute(query="DELETE FROM splits;")
    test_split = Split(db=test_db,name="upper/lower")

    test_split.save()

    test_split.delete()
    assert test_split.name not in test_db.fetchall("SELECT name FROM splits")

# tests for excercise table

def test_excercise_save():
    test_db.execute(query="DELETE FROM exercises;")
    test_excercise = Exercise(test_db,"bench press")

    test_excercise.save()

    assert test_db.fetchall("select name from exercises;") == [("bench press",)]

def test_get_by_name_excercises():
    test_db.execute(query="DELETE FROM exercises;")

    test_excercise = Exercise(test_db,"bench press")
    test_excercise.save()

    temp = Exercise.get_by_name(test_db,"bench press")
    assert temp.name == "bench press"

def test_get_logs_excercises():
    test_db.execute(query="DELETE FROM splits;")
    test_db.execute(query="DELETE FROM workouts;")
    test_db.execute(query="DELETE FROM exercises;")
    test_db.execute(query="DELETE FROM exercise_logs;")

    test_excercise = Exercise(test_db,"bench press")
    test_excercise.save()

    test_split = Split(db=test_db, name="upper/lower")
    test_split.save()

    temp_workout = Workout(test_db, test_split.id, "upper")
    temp_workout.save()

    temp_excercise_logs = ExerciseLog(test_db,temp_workout.id,test_excercise.id,5,4)
    temp_excercise_logs.save()

    get_excercise_logs = test_excercise.get_logs()

    assert get_excercise_logs == [(temp_excercise_logs.id, temp_workout.id, 5, 4)]


def test_delete_excercises():
    test_db.execute(query="DELETE FROM exercises;")
    test_excercise = Exercise(test_db,"bench press")

    test_excercise.save()

    test_excercise.delete()
    assert test_excercise.name not in test_db.fetchall("select name from exercises;")

# tests for workout table

def test_workout_save():

    test_db.execute(query="DELETE FROM splits;")
    test_db.execute(query="DELETE FROM workouts;")

    test_split = Split(test_db, "upper/lower")
    test_split.save()

    test_workout = Workout(test_db, test_split.id, "upper")
    test_workout.save()

    assert test_db.fetchall("SELECT name FROM workouts") == [("upper",)]


def test_get_by_name_workout():

    test_db.execute(query="DELETE FROM splits;")
    test_db.execute(query="DELETE FROM workouts;")

    test_split = Split(test_db, "upper/lower")
    test_split.save()

    test_workout = Workout(test_db, test_split.id, "upper")
    test_workout.save()

    temp = Workout.get_by_name(test_db, test_split.id, "upper")

    assert temp.name == "upper"


def test_get_exercises_workout():

    test_db.execute(query="DELETE FROM splits;")
    test_db.execute(query="DELETE FROM workouts;")
    test_db.execute(query="DELETE FROM exercises;")
    test_db.execute(query="DELETE FROM workout_exercises;")

    test_split = Split(test_db, "upper/lower")
    test_split.save()

    test_workout = Workout(test_db, test_split.id, "upper")
    test_workout.save()

    test_exercise = Exercise(test_db, "bench press")
    test_exercise.save()

    temp_workout_exercise = WorkoutExercise(test_db,test_workout.id,test_exercise.id,3)
    temp_workout_exercise.save()

    get_exercises = test_workout.get_exercises()

    assert get_exercises == [(temp_workout_exercise.id, test_exercise.id, 3)]


def test_get_logs_workout():

    test_db.execute(query="DELETE FROM splits;")
    test_db.execute(query="DELETE FROM workouts;")
    test_db.execute(query="DELETE FROM workout_logs;")

    test_split = Split(test_db, "upper/lower")
    test_split.save()

    test_workout = Workout(test_db, test_split.id, "upper")
    test_workout.save()

    temp_workout_log = WorkoutLog(test_db, test_workout.id, "2026-09-13")
    temp_workout_log.save()

    get_logs = test_workout.get_logs()

    assert get_logs == [(temp_workout_log.id, "2026-09-13")]


def test_delete_workout():

    test_db.execute(query="DELETE FROM splits;")
    test_db.execute(query="DELETE FROM workouts;")

    test_split = Split(test_db, "upper/lower")
    test_split.save()

    test_workout = Workout(test_db, test_split.id, "upper")
    test_workout.save()

    test_workout.delete()

    assert test_workout.name not in test_db.fetchall("SELECT name FROM workouts;")

# tests for workout_exercises table

def test_workout_exercise_save():

    test_db.execute(query="DELETE FROM splits;")
    test_db.execute(query="DELETE FROM workouts;")
    test_db.execute(query="DELETE FROM exercises;")
    test_db.execute(query="DELETE FROM workout_exercises;")

    test_split = Split(test_db, "upper/lower")
    test_split.save()

    test_workout = Workout(test_db, test_split.id, "upper")
    test_workout.save()

    test_exercise = Exercise(test_db, "bench press")
    test_exercise.save()

    test_workout_exercise = WorkoutExercise(test_db,test_workout.id,test_exercise.id,3)
    test_workout_exercise.save()

    assert test_db.fetchall("SELECT exercise_id, sets FROM workout_exercises") == [(test_exercise.id, 3)]


def test_get_by_workout_workout_exercise():

    test_db.execute(query="DELETE FROM splits;")
    test_db.execute(query="DELETE FROM workouts;")
    test_db.execute(query="DELETE FROM exercises;")
    test_db.execute(query="DELETE FROM workout_exercises;")

    test_split = Split(test_db, "upper/lower")
    test_split.save()

    test_workout = Workout(test_db, test_split.id, "upper")
    test_workout.save()

    test_exercise = Exercise(test_db, "bench press")
    test_exercise.save()

    temp_workout_exercise = WorkoutExercise(test_db,test_workout.id,test_exercise.id,3)
    temp_workout_exercise.save()

    get_workout_exercises = WorkoutExercise.get_by_workout(test_db,test_workout.id)

    assert get_workout_exercises == [(temp_workout_exercise.id, test_exercise.id, 3)]


def test_delete_workout_exercise():

    test_db.execute(query="DELETE FROM splits;")
    test_db.execute(query="DELETE FROM workouts;")
    test_db.execute(query="DELETE FROM exercises;")
    test_db.execute(query="DELETE FROM workout_exercises;")

    test_split = Split(test_db, "upper/lower")
    test_split.save()

    test_workout = Workout(test_db, test_split.id, "upper")
    test_workout.save()

    test_exercise = Exercise(test_db, "bench press")
    test_exercise.save()

    test_workout_exercise = WorkoutExercise(test_db,test_workout.id,test_exercise.id,3)
    test_workout_exercise.save()

    test_workout_exercise.delete()

    assert test_db.fetchall("SELECT id FROM workout_exercises") == []

# tests for workout_logs table

def test_workout_log_save():

    test_db.execute(query="DELETE FROM splits;")
    test_db.execute(query="DELETE FROM workouts;")
    test_db.execute(query="DELETE FROM workout_logs;")

    test_split = Split(test_db, "upper/lower")
    test_split.save()

    test_workout = Workout(test_db, test_split.id, "upper")
    test_workout.save()

    test_workout_log = WorkoutLog(test_db,test_workout.id,"2026-09-13")
    test_workout_log.save()

    assert test_db.fetchall("SELECT workout_id, date FROM workout_logs") == [(test_workout.id, "2026-09-13")]


def test_get_by_workout_workout_log():

    test_db.execute(query="DELETE FROM splits;")
    test_db.execute(query="DELETE FROM workouts;")
    test_db.execute(query="DELETE FROM workout_logs;")

    test_split = Split(test_db, "upper/lower")
    test_split.save()

    test_workout = Workout(test_db, test_split.id, "upper")
    test_workout.save()

    temp_workout_log = WorkoutLog(test_db,test_workout.id,"2026-09-13")
    temp_workout_log.save()

    get_workout_logs = WorkoutLog.get_by_workout(test_db,test_workout.id)

    assert get_workout_logs == [(temp_workout_log.id, "2026-09-13")]


def test_get_exercise_logs_workout_log():

    test_db.execute(query="DELETE FROM splits;")
    test_db.execute(query="DELETE FROM workouts;")
    test_db.execute(query="DELETE FROM workout_logs;")
    test_db.execute(query="DELETE FROM exercises;")
    test_db.execute(query="DELETE FROM exercise_logs;")

    test_split = Split(test_db, "upper/lower")
    test_split.save()

    test_workout = Workout(test_db, test_split.id, "upper")
    test_workout.save()

    test_workout_log = WorkoutLog(test_db,test_workout.id,"2026-09-13")
    test_workout_log.save()

    test_exercise = Exercise(test_db, "bench press")
    test_exercise.save()

    temp_exercise_log = ExerciseLog(test_db,test_workout_log.id,test_exercise.id,80,8)
    temp_exercise_log.save()

    get_exercise_logs = test_workout_log.get_exercise_logs()

    assert get_exercise_logs == [(temp_exercise_log.id, test_exercise.id, 80, 8)]


def test_delete_workout_log():

    test_db.execute(query="DELETE FROM splits;")
    test_db.execute(query="DELETE FROM workouts;")
    test_db.execute(query="DELETE FROM workout_logs;")

    test_split = Split(test_db, "upper/lower")
    test_split.save()

    test_workout = Workout(test_db, test_split.id, "upper")
    test_workout.save()

    test_workout_log = WorkoutLog(test_db,test_workout.id,"2026-09-13")
    test_workout_log.save()

    test_workout_log.delete()

    assert test_db.fetchall("SELECT id FROM workout_logs") == []