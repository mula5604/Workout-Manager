import database as db

class Split:
    def __init__(self,name):
        self.name = name
        db.execute("INSERT INTO splits (name) VALUES (?)",(self.name,))

    def remove_split(self):
        db.execute("DELETE FROM splits WHERE name = ?",(self.name,))