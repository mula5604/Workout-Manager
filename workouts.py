import database as db


class Workouts:
    def __init__(self, split_name, name):
        self.name = name

        result = db.execute(
            "SELECT id FROM splits WHERE name = ?",
            (split_name,)
        ).fetchone()

        if result:
            self.split_id = result[0]
        else:
            raise ValueError("Split not found")

        db.execute(
            "INSERT INTO workouts (split_id, name) VALUES (?, ?)",
            (self.split_id, self.name)
        )

    def remove_workout(self):
        db.execute("DELETE FROM workouts WHERE name = ?",(self.name,))