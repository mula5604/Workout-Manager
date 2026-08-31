import database as db
from datetime import date


class Workout_logs:
    def __init__(self,workout_name):
        self.date = date.today()

        workout_id = db.execute("SELECT id FROM workouts WHERE name = ?",(workout_name,)).fetchone()

        if workout_id:
            self.workout_id = workout_id[0]
        else:
            raise ValueError("Workout not found")

        workout_logs_id = db.execute("insert into workout_logs (workout_id,date) values (?,?)",(self.workout_id,self.date,))
        self.workout_logs_id = workout_logs_id.lastrowid

    def delete_workout_logs(self):
        db.execute("delete from workout_logs where id = ?",(self.workout_logs_id,))

        