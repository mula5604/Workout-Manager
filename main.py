import models as m
import database_wrappers as dw
from datetime import date
import sqlite3

database = dw.Database()

def main():

    user_quit = True
    while user_quit:
        print("1 for Splits, 2 for Workouts, 3 for Exercises, 4 for Workout Exercises, any other number to quit")
        user_choice = int(input("Choose a table from the ones above: "))

        match user_choice:
            case 1: # split
                try:
                    add_or_del = int(input("1 to delete a table 2 to add: "))
                    if add_or_del == 2:
                        split_name = str(input("enter name of split: "))
                        my_split = m.Split(database, split_name)
                        my_split.save()
                    else:
                        print(database.fetchall("SELECT name FROM splits;"))
                        split_name = str(input("enter name of split: "))
                        my_split = m.Split.get_by_name(database, split_name)
                        print("deleting")
                        my_split.delete()

                except sqlite3.IntegrityError:
                    print("split already exist")
                    continue

            case 2: # workout
                try:
                    add_or_del = int(input("1 to delete a table 2 to add: "))
                    if add_or_del == 2:
                        print(database.fetchall("SELECT name FROM splits;"))
                        split_name = str(input("enter name of split: "))
                        my_split = m.Split.get_by_name(database, split_name)

                        if my_split == None:
                            print("no such split")
                            continue

                        workout_name = str(input("enter name of workout: "))
                        my_workout = m.Workout(database, my_split.id, workout_name)
                        my_workout.save()

                        my_workout_log = m.WorkoutLog(database, my_workout.id, date.today())
                        my_workout_log.save()
                    else:
                        print(database.fetchall("SELECT name FROM workouts;"))
                        workout_name = str(input("enter name of workout: "))
                        my_workout = m.Workout.get_by_name(database, my_split.id ,workout_name)

                        my_workout.delete()

                except sqlite3.IntegrityError:
                    print("workout already exist")
                    continue


            case 3: # Exercises
                try:
                    add_or_del = int(input("1 to delete a table 2 to add: "))
                    if add_or_del == 2:
                        excercise_name = str(input("enter name of excercise: "))
                        my_excercise = m.Exercise(database, excercise_name)
                        my_excercise.save()
                    else:
                        print(database.fetchall("SELECT name FROM exercises;"))
                        excercise_name = str(input("enter name of exercise: "))
                        my_excercise = m.Exercise.get_by_name(database, excercise_name)

                        my_excercise.delete()

                except sqlite3.IntegrityError:
                    print("excercise already exist")
                    continue

            case 4: # Workout Exercises
                add_or_del = int(input("1 to delete a table 2 to add: "))
                if add_or_del == 2:
                    print(database.fetchall("SELECT name FROM splits;"))
                    split_name = str(input("enter name of split: "))
                    my_split = m.Split.get_by_name(database, split_name)

                    print(database.fetchall("SELECT name FROM workouts;"))
                    workout_name = str(input("enter name of workout: "))
                    my_workout = m.Workout.get_by_name(database, my_split.id ,workout_name)

                    print(database.fetchall("SELECT name FROM exercises;"))
                    excercise_name = str(input("enter name of exercise: "))
                    my_excercise = m.Exercise.get_by_name(database, excercise_name)

                    if my_workout == None or my_excercise == None:
                        print("no such table")
                        continue
                    
                    sets = int(input("how many sets: "))

                    my_we = m.WorkoutExercise(database, my_workout.id, my_excercise.id, sets)
                    my_we.save()

                    for i in range(sets):
                        i += 1
                        reps = int(input(f"how many reps in the {i} set: "))
                        weight = int(input(f"weight moved in the {i} set: "))
                        my_exercise_log = m.ExerciseLog(database, my_workout.id,my_excercise.id, weight, reps)
                        my_exercise_log.save()
                else:
                    print(database.fetchall("SELECT name FROM workouts;"))
                    workout_name = str(input("enter name of workout in which you want to delete something: "))
                    my_workout = m.Workout.get_by_name(database, my_split.id ,workout_name)

                    print(database.fetchall("SELECT name FROM exercises;"))
                    excercise_name = str(input("enter name of exercise in which you want to delete something: "))
                    my_excercise = m.Exercise.get_by_name(database, excercise_name)

                    result = database.fetchone("SELECT id FROM workout_exercises WHERE workout_id = ? AND exercise_id = ?",(my_workout.id, my_excercise.id))

                    if not result:
                        raise ValueError("WorkoutExercise not found")

                    database.delete("DELETE FROM workout_exercises WHERE id = ?",(result[0],))


            case _: # quit
                print("exiting...")
                break


main()