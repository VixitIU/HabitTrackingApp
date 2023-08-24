import sqlite3
from database_operations import with_database_connection


# This function is a decorator that manages database connections for the 'register_user' function.
# It ensures that the 'cursor' parameter is passed as an argument to the wrapped function.

def register_user(username, password):
    with with_database_connection() as cursor:
        # Check if the provided username already exists in the database.
        cursor.execute("SELECT COUNT(*) FROM users WHERE username=?", (username,))
        exists = cursor.fetchone()[0]

        if exists:
            print("Username {} already exists!".format(username))
            return False
        
        # Insert the new user's information into the 'users' table.
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        return True
     

# This function verifies a user's credentials by checking them against the database.
# It takes a username and password as input and returns True if a matching record is found in the 'users' table.
def verify_user(username, password):
    # Establish a database connection and execute a query to retrieve user records.
    with with_database_connection() as cursor:
        # Check if a record with the given username and password exists in the 'users' table.
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        return cursor.fetchone() is not None