import database as db

class workout_excercise:
    def __init__(self,sets,reps,excercise_name,workout_name):
        self.reps = reps
        self.sets = sets
        excercise_id = db.execute("SELECT id FROM excercises WHERE name = ?",(excercise_name,)).fetchone()
        workout_id = db.execute("SELECT id FROM workouts WHERE name = ?",(workout_name,)).fetchone()

        if excercise_id:
            self.excercise_id = excercise_id[0]
        else:
            raise ValueError("Excercise not found")

        if workout_id:
            self.workout_id = workout_id[0]
        else:
            raise ValueError("Workout not found")

        workout_excercise_id = db.execute("INSERT INTO workout_exercises (workout_id, exercise_id,sets,reps) VALUES (?, ?, ?, ?)",(self.workout_id,self.excercise_id,self.sets,self.reps))
        self.workout_excercise_id = workout_excercise_id.lastrowid

    def remove_workout_excercise(self):
        db.execute("delete from workout_exercises where id = ?",(self.workout_excercise_id,))
        