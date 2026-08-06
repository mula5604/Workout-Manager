import sqlite3

conn = sqlite3.connect("workout_db.db")
cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS splits (
    name TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS workouts (
    name TEXT PRIMARY KEY,
    split_name TEXT NOT NULL,
    FOREIGN KEY (split_name) REFERENCES splits(name)
);

CREATE TABLE IF NOT EXISTS exercises (
    name TEXT PRIMARY KEY,
    workout_name TEXT NOT NULL,
    sets INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    FOREIGN KEY (workout_name) REFERENCES workouts(name)
);

CREATE TABLE IF NOT EXISTS workout_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_name TEXT NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (workout_name) REFERENCES workouts(name)
);

CREATE TABLE IF NOT EXISTS sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_id INTEGER NOT NULL,
    exercise_name TEXT NOT NULL,
    set_number INTEGER NOT NULL,
    weight REAL NOT NULL,
    reps INTEGER NOT NULL,
    FOREIGN KEY (log_id) REFERENCES workout_logs(id),
    FOREIGN KEY (exercise_name) REFERENCES exercises(name)
);
""")

conn.commit()
conn.close()

print("Database created successfully!")