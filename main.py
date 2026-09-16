import models as m
import database_wrappers as dw
import datetime

database = dw.Database()

def main():

    split_input = str(input("enter the name of your split: "))
    my_split = m.Split(database,split_input)
    my_split.save()

    workout_input = str(input("enter name of workout: "))
    my_workout = m.Workout(database,my_split.id,workout_input)
    my_workout.save()

    excercise_input = str(input("enter the name of your excercise: "))
    my_excercise = m.Exercise(database,excercise_input)
    my_excercise.save()

    sets = int(input("enter the sets of said excercise: "))
    reps = int(input("enter the reps of said excercise: "))
    weight = int(input("enter the weight of said excercise: "))
    my_workout_excercises = m.WorkoutExercise(database,my_workout.id,my_excercise.id,sets,reps)
    my_workout_excercises.save()

    my_workout_log = m.WorkoutLog(database,my_workout.id,datetime.date.today())
    my_workout_log.save()

    my_excercise_log = m.ExerciseLog(database,my_workout_log.id,my_excercise.id,weight,reps)
    my_excercise_log.save()





main()