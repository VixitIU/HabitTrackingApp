import sqlite3
from database_operations import with_database_connection
import importlib
from datetime import date, datetime



# This function adds a new habit to the database for a given user.
# The 'reminder' parameter can be used to associate a reminder with the habit.
def add_habit(username, title, description, periodicity, reminder):
    with with_database_connection() as cursor:
        # Insert the habit details into the 'habits' table, along with the current creation date.
        cursor.execute(
            "INSERT INTO habits (username, title, description, periodicity, creation_date, streak_broken_date) VALUES (?, ?, ?, ?, datetime('now'), NULL)", 
            (username, title, description, periodicity)
        )
        habit_id = cursor.lastrowid  # Get the ID of the newly inserted habit
        
        if reminder:
            # Insert the reminder details into the 'reminders' table.
            cursor.execute("INSERT INTO reminders (habit_id, next_reminder_time, reminder_frequency) VALUES (?, ?, ?)",
                           (habit_id, reminder.nextReminderTime, reminder.reminderFrequency))




# This function retrieves a list of habits for a specific user from the database.
def get_habits(username, user):
    # Establish a database connection and execute a query to fetch habit records.
    with with_database_connection() as cursor:
        # Import the 'Habit' class from the 'models' module dynamically.
        Habit = importlib.import_module('models').Habit
        
        # Execute a query to retrieve habit records for the given username.
        cursor.execute("SELECT * FROM habits WHERE username=?", (username,))
        rows = cursor.fetchall()

        habits = []
        for row in rows:
            # Create a dictionary to hold habit details from the database row.
            habit_dict = {
                'id': row[0],
                'username': row[1],
                'title': row[2],
                'description': row[3],
                'periodicity': row[4],
                'creation_date': row[5],
                'streak_broken_date': row[6]
            }

            # Convert the streak_broken_date from string to datetime object if it's not None.
            if habit_dict['streak_broken_date']:
                try:
                    # Try parsing as full timestamp
                    streak_broken_date = datetime.strptime(habit_dict['streak_broken_date'], "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    # Fall back to date-only format
                    streak_broken_date = datetime.strptime(habit_dict['streak_broken_date'], "%Y-%m-%d")
            else:
                streak_broken_date = None
            
            # Create a Habit object using the retrieved details and user object.
            habit_obj = Habit(
                habit_id=habit_dict['id'], 
                title=habit_dict['title'], 
                description=habit_dict['description'],
                periodicity=habit_dict['periodicity'],
                user=user,
                streak_broken_date=streak_broken_date  # Use the converted datetime object here
            )

            habits.append(habit_obj)  # Add the Habit object to the list of habits
        
    return habits  # Return the list of Habit objects




# This function marks a habit as complete by recording the completion in the database.
def mark_habit_complete(habit_id, completion_date=None):
    # Establish a database connection and execute a query to record habit completion.
    with with_database_connection() as cursor:
        if completion_date is None:
            # Insert a record into the 'completions' table with the current datetime as the completion date.
            cursor.execute("INSERT INTO completions (habit_id, completion_date) VALUES (?, datetime('now'))", (habit_id,))
        else:
            # Insert a record into the 'completions' table with the provided completion date.
            cursor.execute("INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)", (habit_id, completion_date))


        

def delete_habit(username, title):
   
    with with_database_connection() as cursor:
        # Fetch the habit's ID using the provided username and title.
        cursor.execute("SELECT id FROM habits WHERE username=? AND title=?", (username, title))
        habit_id = cursor.fetchone()
        
        if habit_id:
            habit_id = habit_id[0]
            
            # Delete the habit's completion records from the 'completions' table.
            cursor.execute("DELETE FROM completions WHERE habit_id=?", (habit_id,))
            
            # Delete the habit record from the 'habits' table.
            cursor.execute("DELETE FROM habits WHERE id=?", (habit_id,))
            print(f"Deleted habit with ID: {habit_id}")
        else:
            # Print an error message if the specified habit does not exist.
            print(f"Habit with title {title} does not exist for user {username}.")



        
# This function checks if a habit with a specific title exists for a given user in the database.
def habit_exists_for_user(username, title):
    # Establish a database connection and execute a query to check for the existence of the habit.
    with with_database_connection() as cursor:
        # Execute a query to retrieve habit records with the provided username and title.
        cursor.execute("SELECT * FROM habits WHERE username=? AND title=?", (username, title))
        
        # Return True if a record is found, indicating that the habit exists for the user.
        return cursor.fetchone() is not None
