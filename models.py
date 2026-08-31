class Split:
    def __init__(self, db, name):
        self.db = db
        self.name = name
        self.id = None

    def save(self):
        self.id = self.db.insert("INSERT INTO splits (name) VALUES (?)", (self.name,))
        return self.id

    @classmethod
    def get_by_name(cls, db, name):
        split_id = db.get_id_or_raise("splits", "name", name, f"Split '{name}' not found")
        split = cls(db, name)
        split.id = split_id
        return split

    def get_workouts(self):
        return self.db.execute("SELECT id, name FROM workouts WHERE split_id = ?", (self.id,)).fetchall()

    def delete(self):
        self.db.delete("DELETE FROM splits WHERE id = ?", (self.id,))

class Exercise:
    def __init__(self, db, name):
        self.db = db
        self.name = name
        self.id = None

    def save(self):
        self.id = self.db.insert("INSERT INTO exercises (name) VALUES (?)", (self.name,))
        return self.id

    @classmethod
    def get_by_name(cls, db, name):
        exercise_id = db.get_id_or_raise("exercises", "name", name, f"Exercise '{name}' not found")
        exercise = cls(db, name)
        exercise.id = exercise_id
        return exercise

    def get_logs(self):
        return self.db.execute("SELECT id, workout_log_id, weight, reps FROM exercise_logs WHERE exercise_id = ?", (self.id,)).fetchall()

    def delete(self):
        self.db.delete("DELETE FROM exercises WHERE id = ?", (self.id,))

class Workout:
    def __init__(self, db, split_id, name):
        self.db = db
        self.split_id = split_id
        self.name = name
        self.id = None

    def save(self):
        self.id = self.db.insert("INSERT INTO workouts (split_id, name) VALUES (?, ?)", (self.split_id, self.name))
        return self.id

    @classmethod
    def get_by_name(cls, db, split_id, name):
        result = db.execute("SELECT id FROM workouts WHERE split_id = ? AND name = ?", (split_id, name)).fetchone()
        if not result:
            raise ValueError(f"Workout '{name}' not found")
        workout = cls(db, split_id, name)
        workout.id = result[0]
        return workout

    def get_exercises(self):
        return self.db.execute("SELECT id, exercise_id, sets, reps FROM workout_exercises WHERE workout_id = ?", (self.id,)).fetchall()

    def get_logs(self):
        return self.db.execute("SELECT id, date FROM workout_logs WHERE workout_id = ?", (self.id,)).fetchall()

    def delete(self):
        self.db.delete("DELETE FROM workouts WHERE id = ?", (self.id,))

class WorkoutExercise:
    def __init__(self, db, workout_id, exercise_id, sets, reps):
        self.db = db
        self.workout_id = workout_id
        self.exercise_id = exercise_id
        self.sets = sets
        self.reps = reps
        self.id = None

    def save(self):
        self.id = self.db.insert("INSERT INTO workout_exercises (workout_id, exercise_id, sets, reps) VALUES (?, ?, ?, ?)", (self.workout_id, self.exercise_id, self.sets, self.reps))
        return self.id

    @classmethod
    def get_by_workout(cls, db, workout_id):
        return db.execute("SELECT id, exercise_id, sets, reps FROM workout_exercises WHERE workout_id = ?", (workout_id,)).fetchall()

    def delete(self):
        self.db.delete("DELETE FROM workout_exercises WHERE id = ?", (self.id,))

class WorkoutLog:
    def __init__(self, db, workout_id, date):
        self.db = db
        self.workout_id = workout_id
        self.date = date
        self.id = None

    def save(self):
        self.id = self.db.insert("INSERT INTO workout_logs (workout_id, date) VALUES (?, ?)", (self.workout_id, self.date))
        return self.id

    @classmethod
    def get_by_workout(cls, db, workout_id):
        return db.execute("SELECT id, date FROM workout_logs WHERE workout_id = ?", (workout_id,)).fetchall()

    def get_exercise_logs(self):
        return self.db.execute("SELECT id, exercise_id, weight, reps FROM exercise_logs WHERE workout_log_id = ?", (self.id,)).fetchall()

    def delete(self):
        self.db.delete("DELETE FROM workout_logs WHERE id = ?", (self.id,))
        
class ExerciseLog:
    def __init__(self, db, workout_log_id, exercise_id, weight, reps):
        self.db = db
        self.workout_log_id = workout_log_id
        self.exercise_id = exercise_id
        self.weight = weight
        self.reps = reps
        self.id = None

    def save(self):
        self.id = self.db.insert("INSERT INTO exercise_logs (workout_log_id, exercise_id, weight, reps) VALUES (?, ?, ?, ?)", (self.workout_log_id, self.exercise_id, self.weight, self.reps))
        return self.id

    @classmethod
    def get_by_workout_log(cls, db, workout_log_id):
        return db.execute("SELECT id, exercise_id, weight, reps FROM exercise_logs WHERE workout_log_id = ?", (workout_log_id,)).fetchall()

    def delete(self):
        self.db.delete("DELETE FROM exercise_logs WHERE id = ?", (self.id,))