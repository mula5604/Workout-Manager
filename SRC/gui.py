import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from database_wrappers import Database
from models import (Split,Workout,Exercise,WorkoutExercise,WorkoutLog,ExerciseLog)
class WorkoutManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Workout Manager")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        self.db = Database()
        self.selected_split_id = None
        self.selected_workout_id = None
        self.selected_exercise_id = None
        self.setup_style()
        self.create_gui()
        self.refresh_all()
    def setup_style(self):
        style = ttk.Style()
        try: style.theme_use("clam")
        except tk.TclError: pass
        style.configure("Title.TLabel", font=("Arial", 20, "bold"))
        style.configure("Section.TLabel", font=("Arial", 12, "bold"))
        style.configure("TButton", padding=5)
        style.configure("Treeview", rowheight=28)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
    def create_gui(self):
        title = ttk.Label(self.root, text="Workout Manager", style="Title.TLabel")
        title.pack(pady=10)
        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=10, pady=5)
        split_frame = ttk.LabelFrame(main,text="Splits",padding=8)
        split_frame.grid(row=0,column=0,sticky="nsew",padx=5)
        self.split_list = tk.Listbox(split_frame, height=15)
        self.split_list.pack(fill="both", expand=True)
        self.split_list.bind("<<ListboxSelect>>",self.on_split_selected)
        split_buttons = ttk.Frame(split_frame)
        split_buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(split_buttons,text="Add",command=self.add_split).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(split_buttons,text="Delete",command=self.delete_split).pack(side="left", fill="x", expand=True, padx=2)
        workout_frame = ttk.LabelFrame(main,text="Workouts",padding=8)
        workout_frame.grid(row=0,column=1,sticky="nsew",padx=5)
        self.workout_list = tk.Listbox(workout_frame, height=15)
        self.workout_list.pack(fill="both", expand=True)
        self.workout_list.bind("<<ListboxSelect>>",self.on_workout_selected)
        workout_buttons = ttk.Frame(workout_frame)
        workout_buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(workout_buttons,text="Add",command=self.add_workout).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(workout_buttons,text="Delete",command=self.delete_workout).pack(side="left", fill="x", expand=True, padx=2)
        exercise_frame = ttk.LabelFrame(main,text="Exercises",padding=8)
        exercise_frame.grid(row=0,column=2,sticky="nsew",padx=5)
        self.exercise_list = tk.Listbox(exercise_frame, height=15)
        self.exercise_list.pack(fill="both", expand=True)
        self.exercise_list.bind("<<ListboxSelect>>",self.on_exercise_selected)
        exercise_buttons = ttk.Frame(exercise_frame)
        exercise_buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(exercise_buttons,text="Add",command=self.add_exercise).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(exercise_buttons,text="Delete",command=self.delete_exercise).pack(side="left", fill="x", expand=True, padx=2)
        details_frame = ttk.LabelFrame(self.root,text="Selected Workout",padding=10)
        details_frame.pack(fill="both",expand=True,padx=15,pady=10)
        self.details_label = ttk.Label(details_frame, text="Select a workout")
        self.details_label.pack(anchor="w", pady=(0, 5))
        self.workout_exercises = ttk.Treeview(details_frame,columns=("exercise", "sets"),show="headings",height=5)
        self.workout_exercises.heading("exercise",text="Exercise")
        self.workout_exercises.heading("sets",text="Sets")
        self.workout_exercises.column("exercise",width=300)
        self.workout_exercises.column("sets",width=100,anchor="center")
        self.workout_exercises.pack(fill="both",expand=True)
        bottom_buttons = ttk.Frame(details_frame)
        bottom_buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(bottom_buttons,text="Add Exercise To Workout",command=self.add_exercise_to_workout).pack(side="left", padx=2)
        ttk.Button(bottom_buttons,text="Remove Exercise",command=self.remove_exercise_from_workout).pack(side="left", padx=2)
        ttk.Button(bottom_buttons,text="Start Workout",command=self.start_workout).pack(side="right", padx=2)
        ttk.Button(bottom_buttons,text="History",command=self.show_history).pack(side="right", padx=2)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.columnconfigure(2, weight=1)
        main.rowconfigure(0, weight=1)
    def refresh_all(self):
        self.refresh_splits(); self.refresh_exercises()
    def refresh_splits(self):
        self.split_list.delete(0, tk.END)
        splits = self.db.fetchall("SELECT id, name FROM splits ORDER BY name")
        for split_id, name in splits:
            self.split_list.insert(tk.END, name)
        self.selected_split_id = None
        self.workout_list.delete(0, tk.END)
        self.selected_workout_id = None
        self.clear_workout_details()
    def refresh_workouts(self):
        self.workout_list.delete(0, tk.END)
        if self.selected_split_id is None:
            return
        workouts = self.db.fetchall("""SELECT id, nameFROM workoutsWHERE split_id = ?ORDER BY name""",(self.selected_split_id,))
        for workout_id, name in workouts:
            self.workout_list.insert(tk.END, name)
        self.selected_workout_id = None
        self.clear_workout_details()
    def refresh_exercises(self):
        self.exercise_list.delete(0, tk.END)
        exercises = self.db.fetchall("SELECT id, name FROM exercises ORDER BY name")
        for exercise_id, name in exercises:
            self.exercise_list.insert(tk.END, name)
    def on_split_selected(self, event=None):
        selection = self.split_list.curselection()
        if not selection:
            return
        index = selection[0]
        result = self.db.fetchone("""SELECT idFROM splitsORDER BY name""")
        splits = self.db.fetchall("""SELECT id, nameFROM splitsORDER BY name""")
        self.selected_split_id = splits[index][0]
        self.refresh_workouts()
    def on_workout_selected(self, event=None):
        selection = self.workout_list.curselection()
        if not selection or self.selected_split_id is None:
            return
        index = selection[0]
        workouts = self.db.fetchall("""SELECT id, nameFROM workoutsWHERE split_id = ?ORDER BY name""",(self.selected_split_id,))
        self.selected_workout_id = workouts[index][0]
        self.show_workout_details()
    def on_exercise_selected(self, event=None):
        selection = self.exercise_list.curselection()
        if not selection:
            return
        index = selection[0]
        exercises = self.db.fetchall("""SELECT id, nameFROM exercisesORDER BY name""")
        self.selected_exercise_id = exercises[index][0]
    def add_split(self):
        name = self.ask_for_text("Add Split","Split name:")
        if not name:
            return
        try:
            split = Split(self.db, name)
            split.save()
            self.refresh_splits()
        except Exception as e:
            messagebox.showerror("Error",f"Could not add split:\n\n{e}")
    def delete_split(self):
        if self.selected_split_id is None:
            messagebox.showwarning("No Split","Select a split first.")
            return
        if not messagebox.askyesno("Delete Split","Are you sure you want to delete this split?"):
            return
        try:
            split = Split(self.db,self.get_selected_split_name())
            split.id = self.selected_split_id
            split.delete()
            self.refresh_splits()
        except Exception as e:
            messagebox.showerror("Error",f"Could not delete split:\n\n{e}")
    def get_selected_split_name(self):
        selection = self.split_list.curselection()
        if not selection: return ""
        return self.split_list.get(selection[0])
    def add_workout(self):
        if self.selected_split_id is None:
            messagebox.showwarning("No Split","Select a split first.")
            return
        name = self.ask_for_text("Add Workout","Workout name:")
        if not name:
            return
        try:
            workout = Workout(self.db,self.selected_split_id,name)
            workout.save()
            self.refresh_workouts()
        except Exception as e:
            messagebox.showerror("Error",f"Could not add workout:\n\n{e}")
    def delete_workout(self):
        if self.selected_workout_id is None:
            messagebox.showwarning("No Workout","Select a workout first.")
            return
        if not messagebox.askyesno("Delete Workout","Are you sure you want to delete this workout?"):
            return
        try:
            workout = Workout(self.db,self.selected_split_id,"")
            workout.id = self.selected_workout_id
            workout.delete()
            self.refresh_workouts()
        except Exception as e:
            messagebox.showerror("Error",f"Could not delete workout:\n\n{e}")
    def add_exercise(self):
        name = self.ask_for_text("Add Exercise","Exercise name:")
        if not name:
            return
        try:
            exercise = Exercise(self.db,name)
            exercise.save()
            self.refresh_exercises()
        except Exception as e:
            messagebox.showerror("Error",f"Could not add exercise:\n\n{e}")
    def delete_exercise(self):
        if self.selected_exercise_id is None:
            messagebox.showwarning("No Exercise","Select an exercise first.")
            return
        if not messagebox.askyesno("Delete Exercise","Are you sure you want to delete this exercise?"):
            return
        try:
            exercise = Exercise(self.db,"")
            exercise.id = self.selected_exercise_id
            exercise.delete()
            self.selected_exercise_id = None
            self.refresh_exercises()
        except Exception as e:
            messagebox.showerror("Error",f"Could not delete exercise:\n\n{e}")
    def show_workout_details(self):
        self.workout_exercises.delete(*self.workout_exercises.get_children())
        if self.selected_workout_id is None:
            return
        workout = self.db.fetchone("""SELECT nameFROM workoutsWHERE id = ?""",(self.selected_workout_id,))
        if not workout:
            return
        self.details_label.config(text=f"Workout: {workout[0]}")
        exercises = self.db.fetchall("""SELECTworkout_exercises.id,exercises.name,workout_exercises.setsFROM workout_exercisesJOIN exercisesON exercises.id = workout_exercises.exercise_idWHERE workout_exercises.workout_id = ?ORDER BY workout_exercises.id""",(self.selected_workout_id,))
        for row_id, name, sets in exercises:
            self.workout_exercises.insert("",tk.END,iid=str(row_id),values=(name, sets))
    def clear_workout_details(self):
        self.details_label.config(text="Select a workout"); self.workout_exercises.delete(*self.workout_exercises.get_children())
    def add_exercise_to_workout(self):
        if self.selected_workout_id is None:
            messagebox.showwarning("No Workout","Select a workout first.")
            return
        if self.selected_exercise_id is None:
            messagebox.showwarning("No Exercise","Select an exercise first.")
            return
        sets = self.ask_for_number("Sets","How many sets?")
        if sets is None:
            return
        try:
            workout_exercise = WorkoutExercise(self.db,self.selected_workout_id,self.selected_exercise_id,sets)
            workout_exercise.save()
            self.show_workout_details()
        except Exception as e:
            messagebox.showerror("Error",f"Could not add exercise:\n\n{e}")
    def remove_exercise_from_workout(self):
        selected = self.workout_exercises.selection()
        if not selected:
            messagebox.showwarning("Nothing Selected","Select an exercise from the workout.")
            return
        workout_exercise_id = int(selected[0])
        if not messagebox.askyesno("Remove Exercise","Remove this exercise from the workout?"):
            return
        try:
            workout_exercise = WorkoutExercise(self.db,self.selected_workout_id,0,0)
            workout_exercise.id = workout_exercise_id
            workout_exercise.delete()
            self.show_workout_details()
        except Exception as e:
            messagebox.showerror("Error",f"Could not remove exercise:\n\n{e}")
    def start_workout(self):
        if self.selected_workout_id is None:
            messagebox.showwarning("No Workout","Select a workout first.")
            return
        workout = self.db.fetchone("""SELECT nameFROM workoutsWHERE id = ?""",(self.selected_workout_id,))
        if not workout:
            return
        workout_name = workout[0]
        if not messagebox.askyesno("Start Workout",f"Start '{workout_name}'?"):
            return
        workout_log = WorkoutLog(self.db,self.selected_workout_id,date.today())
        workout_log.save()
        self.open_workout_window(workout_log.id,workout_name)
    def open_workout_window(self, workout_log_id, workout_name):
        window = tk.Toplevel(self.root)
        window.title(f"Workout - {workout_name}")
        window.geometry("700x500")
        window.transient(self.root)
        ttk.Label(window,text=workout_name,style="Title.TLabel").pack(pady=10)
        ttk.Label(window,text=f"Date: {date.today()}").pack()
        frame = ttk.Frame(window)
        frame.pack(fill="both",expand=True,padx=15,pady=15)
        exercises = self.db.fetchall("""SELECTexercises.id,exercises.name,workout_exercises.setsFROM workout_exercisesJOIN exercisesON exercises.id = workout_exercises.exercise_idWHERE workout_exercises.workout_id = ?ORDER BY workout_exercises.id""",(self.selected_workout_id,))
        if not exercises:
            ttk.Label(frame,text="This workout has no exercises yet.").pack()
            return
        entries = []
        for exercise_id, exercise_name, sets in exercises:
            exercise_frame = ttk.LabelFrame(frame,text=f"{exercise_name} ({sets} sets)",padding=8)
            exercise_frame.pack(fill="x",pady=5)
            ttk.Label(exercise_frame,text="Set").grid(row=0, column=0, padx=5)
            ttk.Label(exercise_frame,text="Weight").grid(row=0, column=1, padx=5)
            ttk.Label(exercise_frame,text="Reps").grid(row=0, column=2, padx=5)
            exercise_entries = []
            for set_number in range(1, sets + 1):
                ttk.Label(exercise_frame,text=str(set_number)).grid(row=set_number,column=0,padx=5,pady=2)
                weight_entry = ttk.Entry(exercise_frame,width=10)
                weight_entry.grid(row=set_number,column=1,padx=5,pady=2)
                reps_entry = ttk.Entry(exercise_frame,width=10)
                reps_entry.grid(row=set_number,column=2,padx=5,pady=2)
                exercise_entries.append((weight_entry, reps_entry))
            entries.append((exercise_id, exercise_entries))
        def save_workout():
            try:
                for exercise_id, exercise_entries in entries:
                    for weight_entry, reps_entry in exercise_entries:
                        weight_text = weight_entry.get().strip()
                        reps_text = reps_entry.get().strip()
                        if not weight_text and not reps_text:
                            continue
                        if not weight_text or not reps_text:
                            raise ValueError("Every entered set needs both ""weight and reps.")
                        weight = float(weight_text)
                        reps = int(reps_text)
                        log = ExerciseLog(self.db,workout_log_id,exercise_id,weight,reps)
                        log.save()
                messagebox.showinfo("Workout Complete","Workout saved successfully!")
                window.destroy()
            except ValueError as e:
                messagebox.showerror("Invalid Input",str(e))
            except Exception as e:
                messagebox.showerror("Error",f"Could not save workout:\n\n{e}")
        ttk.Button(window,text="Finish Workout",command=save_workout).pack(pady=10)
    def show_history(self):
        if self.selected_workout_id is None:
            messagebox.showwarning("No Workout","Select a workout first.")
            return
        window = tk.Toplevel(self.root)
        window.title("Workout History")
        window.geometry("700x500")
        ttk.Label(window,text="Workout History",style="Title.TLabel").pack(pady=10)
        logs_tree = ttk.Treeview(window,columns=("date",),show="headings")
        logs_tree.heading("date",text="Date")
        logs_tree.column("date",width=200)
        logs_tree.pack(fill="both",expand=True,padx=15,pady=10)
        logs = self.db.fetchall("""SELECT id, dateFROM workout_logsWHERE workout_id = ?ORDER BY date DESC""",(self.selected_workout_id,))
        for log_id, log_date in logs:
            logs_tree.insert("",tk.END,iid=str(log_id),values=(log_date,))
        def show_log():
            selected = logs_tree.selection()
            if not selected:
                return
            log_id = int(selected[0])
            self.show_log_details(log_id)
        ttk.Button(window,text="View Workout",command=show_log).pack(pady=10)
    def show_log_details(self, log_id):
        window = tk.Toplevel(self.root)
        window.title("Workout Details")
        window.geometry("650x450")
        tree = ttk.Treeview(window,columns=("exercise", "weight", "reps"),show="headings")
        tree.heading("exercise",text="Exercise")
        tree.heading("weight",text="Weight")
        tree.heading("reps",text="Reps")
        tree.column("exercise",width=300)
        tree.column("weight",width=100,anchor="center")
        tree.column("reps",width=100,anchor="center")
        tree.pack(fill="both",expand=True,padx=15,pady=15)
        logs = self.db.fetchall("""SELECTexercises.name,exercise_logs.weight,exercise_logs.repsFROM exercise_logsJOIN exercisesON exercises.id = exercise_logs.exercise_idWHERE exercise_logs.workout_log_id = ?""",(log_id,))
        for exercise, weight, reps in logs:
            tree.insert("",tk.END,values=(exercise, weight, reps))
    def ask_for_text(self, title, prompt):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("350x130")
        window.transient(self.root)
        window.grab_set()
        ttk.Label(window,text=prompt).pack(pady=(15, 5))
        entry = ttk.Entry(window,width=35)
        entry.pack()
        result = {"value": None}
        def submit():
            value = entry.get().strip()
            if value:
                result["value"] = value
            window.destroy()
        ttk.Button(window,text="OK",command=submit).pack(pady=10)
        entry.focus()
        window.bind("<Return>", lambda event: submit())
        self.root.wait_window(window)
        return result["value"]
    def ask_for_number(self, title, prompt):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("350x130")
        window.transient(self.root)
        window.grab_set()
        ttk.Label(window,text=prompt).pack(pady=(15, 5))
        entry = ttk.Entry(window,width=15)
        entry.pack()
        result = {"value": None}
        def submit():
            try:
                value = int(entry.get())
                if value <= 0:
                    raise ValueError
                result["value"] = value
                window.destroy()
            except ValueError:
                messagebox.showerror("Invalid Number","Enter a positive whole number.")
        ttk.Button(window,text="OK",command=submit).pack(pady=10)
        entry.focus()
        window.bind("<Return>", lambda event: submit())
        self.root.wait_window(window)
        return result["value"]
if __name__ == "__main__":
    root = tk.Tk()
    app = WorkoutManagerGUI(root)
    root.mainloop()