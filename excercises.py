import database as db

class Excercises:
    def __init__(self,name):
        self.name = name
        db.execute("INSERT INTO exercises (name) VALUES (?)",(self.name,))

    def remove_excercise(self):
        db.execute("DELETE FROM exercises WHERE name = ?",(self.name,))