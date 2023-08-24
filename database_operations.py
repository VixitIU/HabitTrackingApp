import sqlite3
from functools import wraps
from contextlib import contextmanager

# This context manager provides a convenient way to establish and manage a database connection.
@contextmanager
def with_database_connection():
    """
    A context manager that provides a connection to the SQLite database.
    This context manager ensures that the connection is established, 
    used, and properly closed/committed after use.

    Yields:
        cursor (sqlite3.Cursor): A cursor for executing SQLite commands.
    """
    connection = sqlite3.connect("habits.db")
    cursor = connection.cursor()
    
    try:
        yield cursor  # Provide the cursor for database operations.
    finally:
        connection.commit()  # Save any changes made in the database.
        cursor.close()       # Close the cursor.
        connection.close()   # Terminate the database connection.

def setup_database():
    """
    Set up the SQLite database by creating required tables if they don't exist.
    """
    with with_database_connection() as cursor:
        # Create table for users.
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                         (username TEXT PRIMARY KEY, password TEXT, points INTEGER DEFAULT 0)''')
        
        # Create table for habits.
        cursor.execute('''CREATE TABLE IF NOT EXISTS habits
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, title TEXT, 
                           description TEXT, periodicity TEXT, creation_date DATETIME, 
                           streak_broken_date DATETIME DEFAULT NULL)''')
        
        # Create table for reminders.
        cursor.execute('''CREATE TABLE IF NOT EXISTS reminders
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, habit_id INTEGER, next_reminder_time TEXT, 
                          reminder_frequency TEXT)''')
        
        # Create table to keep track of habit completions.
        cursor.execute('''CREATE TABLE IF NOT EXISTS completions
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, habit_id INTEGER, completion_date DATETIME)''')


def setup_test_environment():
    """
    Set up a test environment by inserting a test user and associated habit 
    into the database for demonstration purposes.

    Returns:
        tuple: Test username and password.
    """
    with with_database_connection() as cursor:
        test_username = "testuser"  # Define test username.
        test_password = "testpass"  # Define test password.
        
        # Insert the test user into the 'users' table.
        cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", (test_username, test_password))
        
        # Insert a test habit for the test user.
        cursor.execute("INSERT OR IGNORE INTO habits (username, title, description, periodicity, creation_date, streak_broken_date) VALUES (?, ?, ?, ?, ?, ?)", 
                       (test_username, "Test Habit", "This is a test habit.", "daily", "2023-04-01", "2023-04-10"))
        
        return test_username, test_password  # Return the credentials for the test user.