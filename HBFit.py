import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import pyodbc
import time
import psycopg2
import os 

class App:
    def __init__(self): 
        self.root = tk.Tk() # Main TK window
        self.root.title("Main Window")
        self.UI_index = self.root # The UI index will mark whatever UI is currently being used
        self.screenmanager = Screenmanager(self.root) # The reference to the screen manager class which handles the GUI transition and attributes
        self.db = Databasemanager() # Database manager class which handles the connection to the database
        self.login = Login(self.root, self.db, self.screenmanager, self) # Login class which handles the login and sign up pages
        self.menumanager = MenuManager(self.screenmanager) # Menu manager class which handles the menu page
        self.settings = Settings(self.screenmanager, self) # Settings class which handles the settings page
        self.nutrition = Nutrition(self.screenmanager, self) # Nutrition class which handles the nutrition page
        self.userID = None # The global user ID 
        
    def loadfunctions(self):
        self.screenmanager.logfunction("login", self.login.loadlogin)
        self.screenmanager.logfunction("menu", self.menumanager.loadmenu)
        self.screenmanager.logfunction("settings", self.settings.firesettings)
        
    
    def startapp(self):
        self.loadfunctions()
        self.login.loadlogin()
        self.root.mainloop()

    def devbypass(self):
        self.userID = 1 
        self.screenmanager.pages["menu"]()
        print("Dev bypass initiated, signed in as user ID:", self.userID, "Welcome, administrator")

class Login:
    def __init__(self, root, db, screenmanager, App): # Login class willl require access to the sreen manager, menu manager and database
        self.screenmanager = screenmanager
        self.root = root
        self.db = db 
        self.app = App

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # LOGIN CLASS WINDOW HANDLERS
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>

    # Load the login page:
    
    def loadlogin(self):
        entry = tk.Toplevel(self.root)
        #entry.attributes("-fullscreen", self.screenmanager.screenstate)
        self.screenmanager.navigate(entry)
        self.app.userID = None
        entry.title("Login Window")
        tk.Label(entry, text="Username:", font=("Ariel", 12)).grid(row=0, column=0) #Creates the username text
        tk.Label(entry, text="Password:", font=("Ariel", 12)).grid(row=1, column=0) #Creates the password text
        Signup_button = tk.Button(entry, text="Sign up", font=("Ariel", 15), command=lambda: self.firesignup())
        Signup_button.grid(row=2, column = 0, pady=10, padx=5)
        user_entry = tk.Entry(entry) # Creates an entry box for the username
        user_entry.grid(row=0,column=1) # Positioons entry box next to username text
        pass_entry = tk.Entry(entry) # Creates an entry box for the password
        pass_entry.grid(row=1, column=1)  # Positions entry box next to password text
        login_button = tk.Button(entry, text="Login", command=lambda: self.login(user_entry, pass_entry), font=("Ariel", 15)) # Defines the login button text and connects it to the login function
        login_button.grid(row=2, column = 1, pady = 10, padx=5) # Positions login box below password 
        #dev button:
        bypass = tk.Button(entry, text="Dev bypass", font=("Ariel", 15), command=lambda: self.app.devbypass()).grid(row=3,columnspan=2, pady=10, padx=5)

    # Load the sign up page:

    def firesignup(self):
        signup = tk.Toplevel(self.root)
        self.screenmanager.navigate(signup)
        self.app.userID = None
        tk.Label(signup, text="Signup credentials:", font=("Ariel", 20, "underline")).grid(row=0, columnspan=2)
        tk.Label(signup, text="Create username:", font=("Ariel", 15)).grid(row=1, column = 0) 
        tk.Label(signup, text="Create password:", font=("Ariel",15)).grid(row=2, column=0) 
        tk.Label(signup, text="Confirm password:", font=("Ariel", 15)).grid(row=3, column=0) 
        tk.Label(signup, text="Metric Information:", font=("Ariel", 20, "underline")).grid(row=4, columnspan=2) 
        tk.Label(signup, text="Age:", font=("Ariel", 15)).grid(row=5, column=0) 
        tk.Label(signup, text="Weight: (KG)", font=("Ariel", 15)).grid(row=6, column=0) 
        tk.Label(signup, text="Gender:", font=("Ariel", 15)).grid(row=7, column=0) 
        signup_username_entry = tk.Entry(signup)
        signup_username_entry.grid(row=1, column=1)
        signup_password_entry = tk.Entry(signup)
        signup_password_entry.grid(row=2, column=1)
        signup_password_confirm = tk.Entry(signup)
        signup_password_confirm.grid(row=3, column=1)
        age_entry = tk.Entry(signup)
        age_entry.grid(row=5, column=1)
        weight_entry = tk.Entry(signup)
        weight_entry.grid(row=6, column=1)
        gender_entry = ttk.Combobox(signup, text="genderselect", state="readonly")
        gender_entry["values"] = ("Male", "Female")
        gender_entry.grid(row=7,column=1)
        footnote = tk.Label(signup, text="Please note: All metric information is used for statistical purposes only", font=("Ariel", 8)).grid(row=8, column=0, columnspan=2)
        return_button = tk.Button(signup, text="Return", font=("Ariel", 15), command=lambda: self.screenmanager.pages["login"](), bd=5).grid(row=9, column=1, pady=15)
        signup_button = tk.Button(signup, text="Create Account", font=("Ariel", 15), bd=5, command=lambda: self.createaccount(signup_username_entry, signup_password_entry, signup_password_confirm, age_entry, weight_entry, gender_entry))
        signup_button.grid(row=9, column=0, pady=15)
        signup.title = "Signup page"

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # LOGIN CLASS FUNCTIONALITY HANDLERS
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # Authenticate login and initialize:

    def login(self, user_entry, pass_entry):
        username = user_entry.get() 
        password = pass_entry.get()
        if username == "" or password == "": 
            print("Input not valid")
            messagebox.showwarning("Input Validation Failed", "Please make sure all fields are filled")
        else:
            connect = self.db.Connect()
            cursor = connect.cursor()
            cursor.execute("SELECT * FROM details WHERE username = %s AND password = %s", (username, password))
            result = cursor.fetchone()
            if result:
                retreiveid = result[0]
                self.app.userID = (retreiveid)
                print("Succesfully validated", username, "with ID:", self.app.userID)
                messagebox.showinfo("Login validated", "You are succesfully logged in!")
                print("Entry UI succesfully withdrawn")
                self.screenmanager.pages["menu"]()
                print("Menu succesfully booted")
            else:
                messagebox.showerror("Login invalid", "Sorry, you failed to log in.")
            self.db.CloseConnect()

    # Add new account to database
        
    def createaccount(self, userentry, userpassword, passwordconfirm, age, weight, gender):
            entry = userentry.get() #values
            password = userpassword.get()
            confirm = passwordconfirm.get()
            age = age.get()
            weight = weight.get()
            gender = gender.get()
            if entry == "" or password == "" or confirm == "" or age == "" or weight == "" or gender == "":
                messagebox.showwarning("Error no input.","Please fill all fields.")
                return
            elif password != confirm:
                messagebox.showwarning("Error input mismatch", "Passwords do not match")
                return
            if age.isdigit() == True:
                age = int(age)
            else:
                messagebox.showwarning("Error bad input", "Age must be a number")
                return
            try:
                weight = float(weight)
            except ValueError:
                messagebox.showwarning("Error bad input", "Weight must be a number or decimal")
                return
            connect = self.db.Connect()
            cursor = connect.cursor()
            cursor.execute("INSERT INTO details (username, password, age, weight, gender) VALUES(%s, %s, %s, %s, %s)", (entry, password, age, weight, gender))
            connect.commit()
            messagebox.showinfo("Sign up complete", "Succesfully signed you up")
            self.db.CloseConnect()
      
class Screenmanager:
    def __init__(self, root):
        self.UI_index = root
        self.screenstate = True
        self.pages = {}
    
    def navigate(self, newui):
        self.UI_index.withdraw()
        self.UI_index = newui
    
    def createtestwindow(self):
        window = tk.Toplevel(self.root)
        FitnessApp.screenmanager.navigate(window)

    def logfunction(self, name, function):
        self.pages[name] = function

    def setupwindow(self, frame):
        pass
    
    def togglescreenstate(self):
        if self.screenstate == True:
            self.screenstate = False
        else:
            self.screenstate = True
        self.UI_index.attributes("-fullscreen", self.screenstate)

class MenuManager:
    def __init__(self, screenmanager):
        self.screenmanager = screenmanager
    
    def loadmenu(self):
        menu = tk.Toplevel()
        self.screenmanager.navigate(menu)
        menu.attributes("-fullscreen", self.screenmanager.screenstate)
        menu.title("Menu Window")
        topframe = tk.Frame(menu)
        topframe.pack(side="top",fill="x")
        print("Menu loaded succesfully")
        tk.Button(topframe, text="☐", command=lambda: self.screenmanager.togglescreenstate()).pack(side="left", padx=10, pady=10) # Exit full screen line
        tk.Button(topframe, text="⚙️", command=lambda: self.screenmanager.pages["settings"]()).pack(side="left", padx=10, pady=10) # Settings opener 
        tk.Label(menu, text="Welcome to HB FIT", font=("Arial", 50)).pack(pady=20)
        tk.Button(menu, text="Workouts", bd=10, font=("Arial", 30), command=lambda: workoutspage()).pack(padx=10, pady=20) # Workouts opener (uncoded)
        tk.Button(menu, text="Nutrition", bd=10 ,font=("Arial", 30), command=lambda:nutritionpage()).pack(padx=10, pady=20) # Nutrition opener
        tk.Button(menu, text="Statistics", bd=10, font=("Ariel", 30), command=lambda:statisticspage()).pack(padx=10, pady=20) # Statistics opener (uncoded)

class Databasemanager:
    def __init__(self):
        self.connect = None

    def Connect(self):
        DATABASE_URL = os.getenv("DATABASE_URL")
        self.connect = psycopg2.connect(DATABASE_URL)
        print("CONNECTION HAS SUCCEEDED")
        return self.connect
    
    def CloseConnect(self):
        self.connect.close()
        self.connect = None
        print("closed connection to db")

class Settings:
    def __init__(self, screenmanager, app):
        self.screenmanager = screenmanager
        self.app = app

    def firesettings(self):
        settings = tk.Toplevel()
        settings.title("Settings window")
        self.screenmanager.navigate(settings)
        settings.attributes("-fullscreen", self.screenmanager.screenstate)
        frame = tk.Frame(settings)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        tk.Label(frame, text="Settings:", font=("Ariel", 20, "underline")).grid(row=0, columnspan=2)
        tk.Label(frame, text="Username:", font=("Ariel", 15)).grid(row=1, column=0, padx=10, pady=10)
        tk.Label(frame, text="Password:", font=("Ariel", 15)).grid(row=2, column=0, padx=10, pady=10)
        tk.Label(frame, text="Sex:", font=("Ariel", 15)).grid(row=5, column=0, padx=10, pady=10)
        tk.Label(frame, text="Age:", font=("Ariel", 15)).grid(row=3, column=0, padx=10, pady=10)
        tk.Label(frame, text="Weight:", font=("Ariel", 15)).grid(row=4, column=0, padx=10, pady=10)
        Username = tk.Entry(frame)
        Username.grid(row=1, column=1, padx=10, pady=10)
        Password = tk.Entry(frame)
        Password.grid(row=2, column=1, padx=10, pady=10)
        Age = tk.Entry(frame)
        Age.grid(row=3, column=1, padx=10, pady=10)
        Weight = tk.Entry(frame)
        Weight.grid(row=4, column=1, padx=10, pady=10)
        Gender = ttk.Combobox(frame, text="Gender", state="readonly")
        Gender["values"] = ("Male", "Female")
        Gender.grid(row=5, column=1, padx=10, pady=10)
        tk.Button(frame, text="Return to menu", command=lambda: self.screenmanager.pages["menu"]()).grid(row=6, column=0, padx=10, pady=20)
        tk.Button(frame, text="Save", command=lambda: self.savesettings(Username, Password, Age, Weight, Gender, self.app.userID)).grid(row=6, column=1, padx=10, pady=20)
        tk.Button(frame, text="Sign out", command=lambda: self.screenmanager.pages["login"]()).grid(row=7, columnspan=2, padx=10, pady=20)
        self.initializedata(Username, Password, Age, Weight, Gender)

    def savesettings(self, Username, Password, Age, Weight, Gender, userid):
        username = Username.get()
        password = Password.get()
        age = Age.get()
        weight = Weight.get()
        gender = Gender.get()
        if username == "" or password == "" or age == "" or weight == "" or gender == "":
            messagebox.showwarning("Error, no input", "Please fill all fields")
            return
        else:
            connect = self.app.db.Connect()
            cursor = connect.cursor()
            cursor.execute("UPDATE details SET username = %s, password = %s, age = %s, weight = %s, gender = %s WHERE ID = %s", (username, password, age, weight, gender, userid))
            connect.commit()
            messagebox.showinfo("Succesfully saved", "Your details have been saved")
            print("Ammended details to database")

    def initializedata(self, Username, Password, Age, Weight, Gender):
        if self.app.userID == None:
            print("Error, no user ID has been found")
            messagebox.showwarning("Error, something went wrong", "Sorry no user ID detected, recommend re sign in")
        else: 
            connect = self.app.db.Connect()
            cursor = connect.cursor()
            cursor.execute("SELECT username, password, age, weight, gender FROM details WHERE ID = %s", (self.app.userID,))
            userdetails = cursor.fetchone()
            if userdetails:
                Username.insert(0, userdetails[0])
                Password.insert(0, userdetails[1])  
                Age.insert(0, userdetails[2])
                Weight.insert(0, userdetails[3])
                Gender.set(userdetails[4])              
            else:
                messagebox.showwarning("Error, something went wrong", "Sorry no user details found, you will need to enter them manually")
    
class Nutrition:
    def __init__(self, screenmanager, app):
        self.screenmanager = screenmanager
        self.app = app 

    def loadnutrition(self):
        nutrition = tk.Toplevel()
        nutrition.title("Nutrition window")
        self.screenmanager.navigate(nutrition)
        nutrition.attributes("-fullscreen", self.screenmanager.screenstate)
        tk.Label(nutrition, text="Nutrition page", font=("Ariel", 20)).pack(pady=20)
        tk.Button(nutrition, text="Return to menu", command=lambda: self.screenmanager.pages["menu"]()).pack(pady=20)
         

FitnessApp = App()
FitnessApp.startapp()