import sqlite3

conn = sqlite3.connect("workout_db.db")
cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS splits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    split_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (split_id) REFERENCES splits(id)
);

CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    sets INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    FOREIGN KEY (workout_id) REFERENCES workouts(id)
);

CREATE TABLE IF NOT EXISTS workout_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (workout_id) REFERENCES workouts(id)
);

CREATE TABLE IF NOT EXISTS sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    set_number INTEGER NOT NULL,
    weight REAL NOT NULL,
    reps INTEGER NOT NULL,
    FOREIGN KEY (log_id) REFERENCES workout_logs(id),
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
);
""")

conn.commit()
conn.close()

print("Database created successfully!")