import time
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from database_wrappers import Database
from models import (Split, Workout, Exercise, WorkoutExercise, WorkoutLog, ExerciseLog)

BG = "#d4d0c8"
FIELD = "#ffffff"
TEXT = "#000000"
MUTED = "#404040"
NAVY = "#000080"
BTN_HOVER = "#e4e0d8"

FONT = ("Tahoma", 9)
FONT_BOLD = ("Tahoma", 9, "bold")
FONT_TITLE = ("Tahoma", 14, "bold")
FONT_SMALL = ("Tahoma", 8)


class WorkoutManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Workout Manager")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG)

        self.db = Database()
        self.ensure_reps_column()

        self.selected_split_id = None
        self.selected_workout_id = None
        self.selected_exercise_id = None

        self.exercise_search = tk.StringVar()
        self.exercise_search.trace_add("write", lambda *a: self.refresh_exercises())

        self.setup_style()
        self.create_gui()
        self.refresh_all()

    def ensure_reps_column(self):
        try:
            columns = [row[1] for row in self.db.fetchall("PRAGMA table_info(workout_exercises)")]
            if "reps" not in columns:
                self.db.execute("ALTER TABLE workout_exercises ADD COLUMN reps INTEGER", ())
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not add reps column:\n\n{e}")

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("classic")
        except tk.TclError:
            pass

        self.root.option_add("*Font", FONT)
        self.root.option_add("*TCombobox*Listbox.background", FIELD)
        self.root.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.root.option_add("*TCombobox*Listbox.selectBackground", NAVY)
        self.root.option_add("*TCombobox*Listbox.selectForeground", "white")

        style.configure(".", background=BG, foreground=TEXT, font=FONT)
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=BG)
        style.configure("TLabelframe", background=BG, borderwidth=2, relief="groove")
        style.configure("TLabelframe.Label", background=BG, foreground=TEXT, font=FONT_BOLD)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("Card.TLabel", background=BG, foreground=TEXT)
        style.configure("Title.TLabel", font=FONT_TITLE, foreground=TEXT)
        style.configure("Subtitle.TLabel", foreground=MUTED)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=FONT_SMALL)
        style.configure("Header.TLabel", background=BG, foreground=TEXT, font=FONT_BOLD)

        for name, font in (("TButton", FONT), ("Accent.TButton", FONT_BOLD),
                           ("Success.TButton", FONT_BOLD)):
            style.configure(name, background=BG, foreground=TEXT, padding=(10, 3),
                            borderwidth=2, font=font)
            style.map(name, background=[("active", BTN_HOVER)])
        style.configure("Small.TButton", background=BG, foreground=TEXT, padding=(4, 1),
                        borderwidth=2, font=FONT_SMALL)
        style.map("Small.TButton", background=[("active", BTN_HOVER)])

        style.configure("Treeview", background=FIELD, fieldbackground=FIELD,
                        foreground=TEXT, rowheight=20, borderwidth=2, relief="sunken")
        style.map("Treeview",
                  background=[("selected", NAVY)],
                  foreground=[("selected", "white")])
        style.configure("Treeview.Heading", background=BG, foreground=TEXT,
                        font=FONT_BOLD, relief="raised", borderwidth=2, padding=3)
        style.map("Treeview.Heading", background=[("active", BTN_HOVER)])

        style.configure("TEntry", fieldbackground=FIELD, foreground=TEXT,
                        insertcolor=TEXT, padding=3, borderwidth=2, relief="sunken")
        style.configure("TCombobox", fieldbackground=FIELD, background=BG,
                        foreground=TEXT, arrowcolor=TEXT, padding=3, borderwidth=2)
        style.map("TCombobox", fieldbackground=[("readonly", FIELD)],
                  foreground=[("readonly", TEXT)])
        style.configure("TSpinbox", fieldbackground=FIELD, foreground=TEXT,
                        arrowcolor=TEXT, padding=3, borderwidth=2)

        style.configure("Vertical.TScrollbar", background=BG, troughcolor="#e8e8e8",
                        arrowcolor=TEXT, borderwidth=2, relief="raised")
        style.map("Vertical.TScrollbar", background=[("active", BTN_HOVER)])

    def make_card(self, parent, title, subtitle=None):
        card = ttk.LabelFrame(parent, text=f" {title} ", padding=8)
        if subtitle:
            ttk.Label(card, text=subtitle, style="Muted.TLabel").pack(anchor="w", pady=(0, 4))
        return card

    def make_list(self, parent, on_select=None, on_double=None):
        wrap = ttk.Frame(parent, style="Card.TFrame")
        wrap.pack(fill="both", expand=True)
        tree = ttk.Treeview(wrap, show="tree", selectmode="browse")
        scroll = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        if on_select:
            tree.bind("<<TreeviewSelect>>", on_select)
        if on_double:
            tree.bind("<Double-1>", on_double)
        return tree

    def button_row(self, parent, buttons):
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x", pady=(10, 0))
        for text, command, style in buttons:
            ttk.Button(row, text=text, command=command, style=style).pack(
                side="left", fill="x", expand=True, padx=3)
        return row

    @staticmethod
    def selected_id(tree):
        sel = tree.selection()
        return int(sel[0]) if sel else None

    def make_modal(self, title, width, height):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=BG)
        win.transient(self.root)
        win.resizable(False, False)
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 3
        win.geometry(f"{width}x{height}+{x}+{y}")
        try:
            win.wait_visibility()
            win.grab_set()
        except tk.TclError:
            pass
        win.bind("<Escape>", lambda e: win.destroy())
        return win

    def create_gui(self):
        header = tk.Frame(self.root, bg=NAVY)
        header.pack(fill="x", padx=3, pady=3)
        tk.Label(header, text="  Workout Manager", bg=NAVY, fg="white",
                 font=FONT_TITLE, pady=6).pack(side="left")
        tk.Label(header, text=date.today().strftime("%A, %d %B %Y") + "  ", bg=NAVY,
                 fg="white", font=FONT).pack(side="right")

        main = ttk.Frame(self.root, padding=(14, 6))
        main.pack(fill="both", expand=True)
        main.columnconfigure((0, 1, 2), weight=1, uniform="cols")
        main.rowconfigure(0, weight=1)

        split_card = self.make_card(main, "Splits")
        split_card.grid(row=0, column=0, sticky="nsew", padx=6)
        self.split_list = self.make_list(split_card, self.on_split_selected)
        self.button_row(split_card, [
            ("+ Add", self.add_split, "Accent.TButton"),
            ("Delete", self.delete_split, "TButton"),
        ])

        workout_card = self.make_card(main, "Workouts")
        workout_card.grid(row=0, column=1, sticky="nsew", padx=6)
        self.workout_list = self.make_list(workout_card, self.on_workout_selected)
        self.button_row(workout_card, [
            ("+ Add", self.add_workout, "Accent.TButton"),
            ("Delete", self.delete_workout, "TButton"),
        ])

        exercise_card = self.make_card(main, "Exercise Library", "double-click to add")
        exercise_card.grid(row=0, column=2, sticky="nsew", padx=6)
        search = ttk.Entry(exercise_card, textvariable=self.exercise_search)
        search.pack(fill="x", pady=(0, 8))
        self.exercise_list = self.make_list(
            exercise_card, self.on_exercise_selected,
            on_double=lambda e: self.add_exercise_to_workout())
        self.button_row(exercise_card, [
            ("+ Add", self.add_exercise, "Accent.TButton"),
            ("Delete", self.delete_exercise, "TButton"),
        ])

        details = self.make_card(self.root, "Selected Workout")
        details.pack(fill="both", expand=True, padx=20, pady=(8, 16))

        self.details_label = ttk.Label(details, text="Select a workout",
                                       style="Muted.TLabel")
        self.details_label.pack(anchor="w", pady=(0, 6))

        tree_wrap = ttk.Frame(details, style="Card.TFrame")
        tree_wrap.pack(fill="both", expand=True)
        self.workout_exercises = ttk.Treeview(
            tree_wrap, columns=("exercise", "sets", "reps"), show="headings",
            height=5, selectmode="browse")
        self.workout_exercises.heading("exercise", text="Exercise", anchor="w")
        self.workout_exercises.heading("sets", text="Sets")
        self.workout_exercises.heading("reps", text="Reps")
        self.workout_exercises.column("exercise", width=400, anchor="w")
        self.workout_exercises.column("sets", width=100, anchor="center")
        self.workout_exercises.column("reps", width=100, anchor="center")
        wscroll = ttk.Scrollbar(tree_wrap, orient="vertical",
                                command=self.workout_exercises.yview)
        self.workout_exercises.configure(yscrollcommand=wscroll.set)
        self.workout_exercises.pack(side="left", fill="both", expand=True)
        wscroll.pack(side="right", fill="y")

        bottom = ttk.Frame(details, style="Card.TFrame")
        bottom.pack(fill="x", pady=(10, 0))
        ttk.Button(bottom, text="+ Add Exercise To Workout",
                   command=self.add_exercise_to_workout).pack(side="left", padx=(0, 6))
        ttk.Button(bottom, text="Remove Exercise",
                   command=self.remove_exercise_from_workout).pack(side="left", padx=6)
        ttk.Button(bottom, text="▶  Start Workout", style="Success.TButton",
                   command=self.start_workout).pack(side="right", padx=(6, 0))
        ttk.Button(bottom, text="History",
                   command=self.show_history).pack(side="right", padx=6)

    def refresh_all(self):
        self.refresh_splits()
        self.refresh_exercises()

    def refresh_splits(self, select_id=None):
        self.split_list.delete(*self.split_list.get_children())

        for split_id, name in self.db.fetchall("SELECT id,name FROM splits ORDER BY name"):
            self.split_list.insert("", tk.END, iid=str(split_id), text="  " + name)

        self.selected_split_id = None
        self.selected_workout_id = None
        self.workout_list.delete(*self.workout_list.get_children())
        self.clear_workout_details()

        if select_id is not None and self.split_list.exists(str(select_id)):
            self.selected_split_id = select_id
            self.split_list.selection_set(str(select_id))
            self.refresh_workouts()

    def refresh_workouts(self, select_id=None):
        self.workout_list.delete(*self.workout_list.get_children())
        self.selected_workout_id = None
        self.clear_workout_details()

        if self.selected_split_id is None:
            return

        workouts = self.db.fetchall(
            "SELECT id,name FROM workouts WHERE split_id = ? ORDER BY name",
            (self.selected_split_id,))
        for workout_id, name in workouts:
            self.workout_list.insert("", tk.END, iid=str(workout_id), text="  " + name)

        if select_id is not None and self.workout_list.exists(str(select_id)):
            self.selected_workout_id = select_id
            self.workout_list.selection_set(str(select_id))
            self.show_workout_details()

    def refresh_exercises(self):
        keep = self.selected_exercise_id
        self.exercise_list.delete(*self.exercise_list.get_children())

        query = self.exercise_search.get().strip()
        exercises = self.db.fetchall(
            "SELECT id,name FROM exercises WHERE name LIKE ? ORDER BY name",
            (f"%{query}%",))
        for exercise_id, name in exercises:
            self.exercise_list.insert("", tk.END, iid=str(exercise_id), text="  " + name)

        if keep is not None and self.exercise_list.exists(str(keep)):
            self.exercise_list.selection_set(str(keep))
        else:
            self.selected_exercise_id = None

    def on_split_selected(self, event=None):
        split_id = self.selected_id(self.split_list)
        if split_id is None or split_id == self.selected_split_id:
            return
        self.selected_split_id = split_id
        self.refresh_workouts()

    def on_workout_selected(self, event=None):
        workout_id = self.selected_id(self.workout_list)
        if workout_id is None or workout_id == self.selected_workout_id:
            return
        self.selected_workout_id = workout_id
        self.show_workout_details()

    def on_exercise_selected(self, event=None):
        exercise_id = self.selected_id(self.exercise_list)
        if exercise_id is not None:
            self.selected_exercise_id = exercise_id

    def add_split(self):
        name = self.ask_for_text("Add Split", "Split name:")
        if not name:
            return
        try:
            split = Split(self.db, name)
            split.save()
            self.refresh_splits(select_id=split.id)
        except Exception as e:
            messagebox.showerror("Error", f"Could not add split:\n\n{e}")

    def delete_split(self):
        if self.selected_split_id is None:
            messagebox.showwarning("No Split", "Select a split first.")
            return
        if not messagebox.askyesno("Delete Split",
                                   "Are you sure you want to delete this split?"):
            return
        try:
            split = Split(self.db, self.get_selected_split_name())
            split.id = self.selected_split_id
            split.delete()
            self.refresh_splits()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete split:\n\n{e}")

    def get_selected_split_name(self):
        sel = self.split_list.selection()
        return self.split_list.item(sel[0], "text").strip() if sel else ""

    def add_workout(self):
        if self.selected_split_id is None:
            messagebox.showwarning("No Split", "Select a split first.")
            return
        name = self.ask_for_text("Add Workout", "Workout name:")
        if not name:
            return
        try:
            workout = Workout(self.db, self.selected_split_id, name)
            workout.save()
            self.refresh_workouts(select_id=workout.id)
        except Exception as e:
            messagebox.showerror("Error", f"Could not add workout:\n\n{e}")

    def delete_workout(self):
        if self.selected_workout_id is None:
            messagebox.showwarning("No Workout", "Select a workout first.")
            return
        if not messagebox.askyesno("Delete Workout",
                                   "Are you sure you want to delete this workout?"):
            return
        try:
            workout = Workout(self.db, self.selected_split_id, "")
            workout.id = self.selected_workout_id
            workout.delete()
            self.refresh_workouts()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete workout:\n\n{e}")

    def add_exercise(self):
        name = self.ask_for_text("Add Exercise", "Exercise name:")
        if not name:
            return
        try:
            exercise = Exercise(self.db, name)
            exercise.save()
            self.exercise_search.set("")
            self.selected_exercise_id = exercise.id
            self.refresh_exercises()
            if self.exercise_list.exists(str(exercise.id)):
                self.exercise_list.see(str(exercise.id))
        except Exception as e:
            messagebox.showerror("Error", f"Could not add exercise:\n\n{e}")

    def delete_exercise(self):
        if self.selected_exercise_id is None:
            messagebox.showwarning("No Exercise", "Select an exercise first.")
            return
        if not messagebox.askyesno("Delete Exercise",
                                   "Are you sure you want to delete this exercise?"):
            return
        try:
            exercise = Exercise(self.db, "")
            exercise.id = self.selected_exercise_id
            exercise.delete()
            self.selected_exercise_id = None
            self.refresh_exercises()
            self.show_workout_details()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete exercise:\n\n{e}")

    def show_workout_details(self):
        self.workout_exercises.delete(*self.workout_exercises.get_children())

        if self.selected_workout_id is None:
            return

        workout = self.db.fetchone("SELECT name FROM workouts WHERE id = ?",
                                   (self.selected_workout_id,))
        if not workout:
            return

        exercises = self.db.fetchall(
            """SELECT workout_exercises.id,
            exercises.name,
            workout_exercises.sets,
            workout_exercises.reps
            FROM workout_exercises
            JOIN exercises
            ON exercises.id = workout_exercises.exercise_id
            WHERE workout_exercises.workout_id = ?
            ORDER BY workout_exercises.id""",
            (self.selected_workout_id,))

        total_sets = 0
        for row_id, name, sets, reps in exercises:
            self.workout_exercises.insert("", tk.END, iid=str(row_id),
                                          values=(name, sets, reps if reps else "—"))
            try:
                total_sets += int(sets)
            except (TypeError, ValueError):
                pass

        self.details_label.config(
            text=f"{workout[0]}   •   {len(exercises)} exercises   •   {total_sets} sets")

    def clear_workout_details(self):
        self.details_label.config(text="Select a workout")
        self.workout_exercises.delete(*self.workout_exercises.get_children())

    def add_exercise_to_workout(self):
        if self.selected_workout_id is None:
            messagebox.showwarning("No Workout", "Select a workout first.")
            return

        choice = self.ask_exercise_and_sets()
        if choice is None:
            return
        exercise_id, sets, reps = choice

        try:
            WorkoutExercise(self.db, self.selected_workout_id, exercise_id, sets, reps).save()
            self.show_workout_details()
        except Exception as e:
            messagebox.showerror("Error", f"Could not add exercise:\n\n{e}")

    def ask_exercise_and_sets(self):
        exercises = self.db.fetchall("SELECT id,name FROM exercises ORDER BY name")
        if not exercises:
            messagebox.showwarning("No Exercises", "Create an exercise first.")
            return None

        ids = [e[0] for e in exercises]
        names = [e[1] for e in exercises]

        win = self.make_modal("Add Exercise To Workout", 400, 290)
        body = ttk.Frame(win, padding=20)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text="Exercise").pack(anchor="w")
        combo = ttk.Combobox(body, values=names, state="readonly")
        combo.pack(fill="x", pady=(4, 12))
        if self.selected_exercise_id in ids:
            combo.current(ids.index(self.selected_exercise_id))
        else:
            combo.current(0)

        numbers = ttk.Frame(body)
        numbers.pack(fill="x", pady=(0, 14))

        sets_box = ttk.Frame(numbers)
        sets_box.pack(side="left", padx=(0, 24))
        ttk.Label(sets_box, text="Sets").pack(anchor="w")
        sets_var = tk.StringVar(value="3")
        ttk.Spinbox(sets_box, from_=1, to=30, textvariable=sets_var, width=8).pack(pady=(4, 0))

        reps_box = ttk.Frame(numbers)
        reps_box.pack(side="left")
        ttk.Label(reps_box, text="Reps per set").pack(anchor="w")
        reps_var = tk.StringVar(value="10")
        ttk.Spinbox(reps_box, from_=1, to=100, textvariable=reps_var, width=8).pack(pady=(4, 0))

        result = {"value": None}

        def submit(event=None):
            try:
                sets = int(sets_var.get())
                reps = int(reps_var.get())
                if sets <= 0 or reps <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Number", "Sets and reps must be positive whole numbers.",
                                     parent=win)
                return
            result["value"] = (ids[combo.current()], sets, reps)
            win.destroy()

        btns = ttk.Frame(body)
        btns.pack(fill="x")
        ttk.Button(btns, text="Cancel", command=win.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(btns, text="Add", style="Accent.TButton", command=submit).pack(side="right")
        win.bind("<Return>", submit)

        self.root.wait_window(win)
        return result["value"]

    def remove_exercise_from_workout(self):
        selected = self.workout_exercises.selection()
        if not selected:
            messagebox.showwarning("Nothing Selected",
                                   "Select an exercise from the workout.")
            return
        if not messagebox.askyesno("Remove Exercise",
                                   "Remove this exercise from the workout?"):
            return
        try:
            workout_exercise = WorkoutExercise(self.db, self.selected_workout_id, 0, 0)
            workout_exercise.id = int(selected[0])
            workout_exercise.delete()
            self.show_workout_details()
        except Exception as e:
            messagebox.showerror("Error", f"Could not remove exercise:\n\n{e}")

    def start_workout(self):
        if self.selected_workout_id is None:
            messagebox.showwarning("No Workout", "Select a workout first.")
            return

        workout = self.db.fetchone("SELECT name FROM workouts WHERE id = ?",
                                   (self.selected_workout_id,))
        if not workout:
            return

        self.open_workout_window(self.selected_workout_id, workout[0])

    def get_last_sets(self, exercise_id):
        try:
            last = self.db.fetchone(
                """SELECT exercise_logs.workout_log_id
                FROM exercise_logs
                JOIN workout_logs ON workout_logs.id = exercise_logs.workout_log_id
                WHERE exercise_logs.exercise_id = ?
                ORDER BY workout_logs.date DESC, workout_logs.id DESC
                LIMIT 1""",
                (exercise_id,))
            if not last:
                return []
            return self.db.fetchall(
                """SELECT weight, reps FROM exercise_logs
                WHERE workout_log_id = ? AND exercise_id = ?
                ORDER BY id""",
                (last[0], exercise_id))
        except Exception:
            return []

    @staticmethod
    def fmt_weight(weight):
        try:
            return f"{float(weight):g}"
        except (TypeError, ValueError):
            return str(weight)

    def open_workout_window(self, workout_id, workout_name):
        window = tk.Toplevel(self.root)
        window.title(f"Workout - {workout_name}")
        window.geometry("860x760")
        window.minsize(700, 500)
        window.configure(bg=BG)
        window.transient(self.root)

        started = time.time()

        top = ttk.Frame(window, padding=(20, 14, 20, 6))
        top.pack(fill="x")
        left = ttk.Frame(top)
        left.pack(side="left")
        ttk.Label(left, text=workout_name, style="Title.TLabel").pack(anchor="w")
        ttk.Label(left, text=date.today().strftime("%A, %d %B %Y"),
                  style="Subtitle.TLabel").pack(anchor="w")
        timer_label = tk.Label(top, text="00:00", bg="black", fg="#00ff00",
                               font=("Courier New", 16, "bold"), padx=8, pady=2,
                               relief="sunken", bd=2)
        timer_label.pack(side="right")

        def tick():
            try:
                if not window.winfo_exists():
                    return
                elapsed = int(time.time() - started)
                h, rem = divmod(elapsed, 3600)
                m, s = divmod(rem, 60)
                timer_label.config(text=f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}")
                window.after(1000, tick)
            except tk.TclError:
                pass

        tick()

        exercises = self.db.fetchall(
            """SELECT exercises.id,
            exercises.name,
            workout_exercises.sets,
            workout_exercises.reps
            FROM workout_exercises
            JOIN exercises
            ON exercises.id = workout_exercises.exercise_id
            WHERE workout_exercises.workout_id = ?
            ORDER BY workout_exercises.id""",
            (workout_id,))

        footer = ttk.Frame(window, padding=(20, 10, 20, 14))
        footer.pack(side="bottom", fill="x")

        if not exercises:
            ttk.Label(window, text="No exercises have been added to this workout.",
                      style="Subtitle.TLabel").pack(pady=40)
            ttk.Button(footer, text="Close", command=window.destroy).pack(side="right")
            return

        body = ttk.Frame(window, padding=(14, 0))
        body.pack(fill="both", expand=True)

        canvas = tk.Canvas(body, bg=BG, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfigure(win_id, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_wheel(event):
            if event.num == 4:
                canvas.yview_scroll(-2, "units")
            elif event.num == 5:
                canvas.yview_scroll(2, "units")
            else:
                canvas.yview_scroll(int(-event.delta / 120) * 2, "units")

        window.bind("<MouseWheel>", on_wheel)
        window.bind("<Button-4>", on_wheel)
        window.bind("<Button-5>", on_wheel)

        def focus_next(event):
            nxt = event.widget.tk_focusNext()
            if nxt:
                nxt.focus_set()
                try:
                    nxt.select_range(0, tk.END)
                except (tk.TclError, AttributeError):
                    pass
            return "break"

        cards = []

        for exercise_id, exercise_name, sets, target_reps in exercises:
            try:
                sets = int(sets)
            except (TypeError, ValueError):
                sets = 0

            last_sets = self.get_last_sets(exercise_id)

            card = ttk.LabelFrame(inner, text=f" {exercise_name} ", padding=10)
            card.pack(fill="x", padx=6, pady=6)

            head = ttk.Frame(card, style="Card.TFrame")
            head.pack(fill="x")
            target = f"{sets} sets × {target_reps} reps" if target_reps else f"{sets} sets"
            ttk.Label(head, text=target, style="Muted.TLabel").pack(side="left")

            grid = ttk.Frame(card, style="Card.TFrame")
            grid.pack(fill="x", pady=(10, 0))
            grid.columnconfigure(1, weight=1)

            for col, text in enumerate(("SET", "LAST TIME", "WEIGHT (KG)", "REPS", "")):
                ttk.Label(grid, text=text, style="Header.TLabel").grid(
                    row=0, column=col, padx=8, pady=(0, 6), sticky="w" if col == 1 else "")

            data = {"id": exercise_id, "name": exercise_name, "rows": []}
            cards.append(data)

            def add_row(data=data, grid=grid, last_sets=last_sets):
                index = len(data["rows"])
                r = index + 1

                set_label = ttk.Label(grid, text=str(r), style="Card.TLabel",
                                      font=FONT_BOLD, width=4, anchor="center")
                set_label.grid(row=r, column=0, padx=8, pady=4)

                if index < len(last_sets):
                    lw, lr = last_sets[index]
                    prev_text = f"{self.fmt_weight(lw)} kg × {lr}"
                else:
                    lw = lr = None
                    prev_text = "—"
                prev_label = ttk.Label(grid, text=prev_text, style="Muted.TLabel")
                prev_label.grid(row=r, column=1, padx=8, sticky="w")

                weight_entry = ttk.Entry(grid, width=12, justify="center")
                weight_entry.grid(row=r, column=2, padx=8, pady=4)
                reps_entry = ttk.Entry(grid, width=10, justify="center")
                reps_entry.grid(row=r, column=3, padx=8, pady=4)

                for entry in (weight_entry, reps_entry):
                    entry.bind("<Return>", focus_next)

                fill_btn = None
                if lw is not None:
                    def fill(we=weight_entry, re=reps_entry, w=lw, rp=lr):
                        we.delete(0, tk.END)
                        we.insert(0, self.fmt_weight(w))
                        re.delete(0, tk.END)
                        re.insert(0, str(rp))
                    fill_btn = ttk.Button(grid, text="↺ copy", style="Small.TButton",
                                          command=fill, takefocus=False)
                    fill_btn.grid(row=r, column=4, padx=8)

                data["rows"].append({
                    "weight": weight_entry,
                    "reps": reps_entry,
                    "widgets": [set_label, prev_label, weight_entry, reps_entry, fill_btn],
                })

            def remove_row(data=data):
                if not data["rows"]:
                    return
                row = data["rows"].pop()
                for w in row["widgets"]:
                    if w is not None:
                        w.destroy()

            controls = ttk.Frame(card, style="Card.TFrame")
            controls.pack(fill="x", pady=(8, 0))
            ttk.Button(controls, text="+ Add Set", style="Small.TButton",
                       command=add_row, takefocus=False).pack(side="left")
            ttk.Button(controls, text="– Remove Set", style="Small.TButton",
                       command=remove_row, takefocus=False).pack(side="left", padx=6)

            for _ in range(max(sets, 1)):
                add_row()

        def has_input():
            for c in cards:
                for row in c["rows"]:
                    if row["weight"].get().strip() or row["reps"].get().strip():
                        return True
            return False

        def cancel():
            if has_input() and not messagebox.askyesno(
                    "Discard Workout", "Discard this workout without saving?",
                    parent=window):
                return
            window.destroy()

        def save_workout():
            to_save = []
            try:
                for c in cards:
                    for number, row in enumerate(c["rows"], start=1):
                        weight_text = row["weight"].get().strip().replace(",", ".")
                        reps_text = row["reps"].get().strip()

                        if not weight_text and not reps_text:
                            continue

                        where = f"{c['name']} – set {number}: "
                        if not weight_text:
                            raise ValueError(where + "enter a weight (0 for bodyweight).")
                        if not reps_text:
                            raise ValueError(where + "enter reps.")

                        try:
                            weight = float(weight_text)
                            reps = int(reps_text)
                        except ValueError:
                            raise ValueError(where + "weight must be a number and reps a whole number.")

                        if weight < 0:
                            raise ValueError(where + "weight cannot be negative.")
                        if reps <= 0:
                            raise ValueError(where + "reps must be greater than 0.")

                        to_save.append((c["id"], weight, reps))

                if not to_save:
                    raise ValueError("Enter at least one set before finishing.")

                workout_log = WorkoutLog(self.db, workout_id, date.today())
                workout_log.save()

                for exercise_id, weight, reps in to_save:
                    ExerciseLog(self.db, workout_log.id, exercise_id, weight, reps).save()

                messagebox.showinfo("Workout Complete",
                                    f"Saved {len(to_save)} sets. Nice work!",
                                    parent=window)
                window.destroy()

            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e), parent=window)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save workout:\n\n{e}",
                                     parent=window)

        ttk.Button(footer, text="Cancel", command=cancel).pack(side="left")
        ttk.Button(footer, text="✔  FINISH WORKOUT", style="Success.TButton",
                   command=save_workout).pack(side="right")

        window.protocol("WM_DELETE_WINDOW", cancel)

    def show_history(self):
        if self.selected_workout_id is None:
            messagebox.showwarning("No Workout", "Select a workout first.")
            return

        window = tk.Toplevel(self.root)
        window.title("Workout History")
        window.geometry("560x480")
        window.configure(bg=BG)
        window.transient(self.root)

        ttk.Label(window, text="Workout History", style="Title.TLabel").pack(
            pady=(16, 8), padx=20, anchor="w")

        wrap = ttk.Frame(window, padding=(20, 0))
        wrap.pack(fill="both", expand=True)

        logs_tree = ttk.Treeview(wrap, columns=("date", "sets"), show="headings",
                                 selectmode="browse")
        logs_tree.heading("date", text="Date", anchor="w")
        logs_tree.heading("sets", text="Sets logged")
        logs_tree.column("date", width=250, anchor="w")
        logs_tree.column("sets", width=120, anchor="center")
        scroll = ttk.Scrollbar(wrap, orient="vertical", command=logs_tree.yview)
        logs_tree.configure(yscrollcommand=scroll.set)
        logs_tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        logs = self.db.fetchall(
            """SELECT workout_logs.id, workout_logs.date,
            COUNT(exercise_logs.workout_log_id)
            FROM workout_logs
            LEFT JOIN exercise_logs
            ON exercise_logs.workout_log_id = workout_logs.id
            WHERE workout_logs.workout_id = ?
            GROUP BY workout_logs.id
            ORDER BY workout_logs.date DESC, workout_logs.id DESC""",
            (self.selected_workout_id,))

        for log_id, log_date, count in logs:
            logs_tree.insert("", tk.END, iid=str(log_id), values=(log_date, count))

        def show_log(event=None):
            log_id = self.selected_id(logs_tree)
            if log_id is not None:
                self.show_log_details(log_id)

        logs_tree.bind("<Double-1>", show_log)

        footer = ttk.Frame(window, padding=(20, 12))
        footer.pack(fill="x")
        ttk.Button(footer, text="Close", command=window.destroy).pack(side="right")
        ttk.Button(footer, text="View Workout", style="Accent.TButton",
                   command=show_log).pack(side="right", padx=6)

    def show_log_details(self, log_id):
        window = tk.Toplevel(self.root)
        window.title("Workout Details")
        window.geometry("620x500")
        window.configure(bg=BG)
        window.transient(self.root)

        logs = self.db.fetchall(
            """SELECT exercises.name,
            exercise_logs.weight,
            exercise_logs.reps
            FROM exercise_logs
            JOIN exercises
            ON exercises.id = exercise_logs.exercise_id
            WHERE exercise_logs.workout_log_id = ?
            ORDER BY exercise_logs.id""",
            (log_id,))

        volume = 0.0
        for _, weight, reps in logs:
            try:
                volume += float(weight) * int(reps)
            except (TypeError, ValueError):
                pass

        ttk.Label(window, text="Workout Details", style="Title.TLabel").pack(
            pady=(16, 0), padx=20, anchor="w")
        ttk.Label(window, text=f"{len(logs)} sets   •   {volume:,.0f} kg total volume",
                  style="Subtitle.TLabel").pack(padx=20, anchor="w", pady=(0, 8))

        wrap = ttk.Frame(window, padding=(20, 0, 20, 16))
        wrap.pack(fill="both", expand=True)

        tree = ttk.Treeview(wrap, columns=("exercise", "set", "weight", "reps"),
                            show="headings")
        for col, text, width, anchor in (
                ("exercise", "Exercise", 260, "w"),
                ("set", "Set", 60, "center"),
                ("weight", "Weight (kg)", 100, "center"),
                ("reps", "Reps", 80, "center")):
            tree.heading(col, text=text, anchor=anchor)
            tree.column(col, width=width, anchor=anchor)
        scroll = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        counters = {}
        for exercise, weight, reps in logs:
            counters[exercise] = counters.get(exercise, 0) + 1
            tree.insert("", tk.END,
                        values=(exercise, counters[exercise], self.fmt_weight(weight), reps))

    def ask_for_text(self, title, prompt):
        win = self.make_modal(title, 380, 170)
        body = ttk.Frame(win, padding=20)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text=prompt).pack(anchor="w")
        entry = ttk.Entry(body)
        entry.pack(fill="x", pady=(6, 14))
        entry.focus_set()

        result = {"value": None}

        def submit(event=None):
            value = entry.get().strip()
            if value:
                result["value"] = value
            win.destroy()

        btns = ttk.Frame(body)
        btns.pack(fill="x")
        ttk.Button(btns, text="Cancel", command=win.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(btns, text="OK", style="Accent.TButton", command=submit).pack(side="right")
        win.bind("<Return>", submit)

        self.root.wait_window(win)
        return result["value"]

    def ask_for_number(self, title, prompt):
        win = self.make_modal(title, 380, 170)
        body = ttk.Frame(win, padding=20)
        body.pack(fill="both", expand=True)

        ttk.Label(body, text=prompt).pack(anchor="w")
        entry = ttk.Entry(body, width=15)
        entry.pack(anchor="w", pady=(6, 14))
        entry.focus_set()

        result = {"value": None}

        def submit(event=None):
            try:
                value = int(entry.get())
                if value <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Number", "Enter a positive whole number.",
                                     parent=win)
                return
            result["value"] = value
            win.destroy()

        btns = ttk.Frame(body)
        btns.pack(fill="x")
        ttk.Button(btns, text="Cancel", command=win.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(btns, text="OK", style="Accent.TButton", command=submit).pack(side="right")
        win.bind("<Return>", submit)

        self.root.wait_window(win)
        return result["value"]


if __name__ == "__main__":
    root = tk.Tk()
    app = WorkoutManagerGUI(root)
    root.mainloop()