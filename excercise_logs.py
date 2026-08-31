import database as db

class exercise_log:
    def __init__(self,workout_log_id,weight,reps,excercise_name):
        self.workout_log_id = workout_log_id
        self.weight = weight
        self.reps = reps

        excercise_id = db.execute("SELECT id FROM exercises WHERE name = ?",(excercise_name,)).fetchone()

        if excercise_id:
            self.excercise_id = excercise_id[0]
        else:
            raise ValueError("Excercise not found")

        exercise_log_id = db.execute("INSERT INTO exercise_logs (workout_log_id, exercise_id, weight, reps) VALUES (?, ?, ?, ?)",(self.workout_log_id,self.excercise_id,self.weight,self.reps))
        self.exercise_log_id = exercise_log_id.lastrowid

    def remove_exercise_log(self):
        db.execute("DELETE FROM exercise_logs WHERE id = ?",(self.exercise_log_id,))