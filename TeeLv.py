import datetime
import random
from habit_operations import mark_habit_complete
from models import User, SessionManager, Habit, Analytics, Reminder, Reward
from database_operations import with_database_connection

def populate_TeeLv_habits_and_reminders(username):
    # Details for the habits and their respective reminders
    habits_and_reminders = [
        ("Morning Run", "Run for 30 minutes every morning", "daily", None, None),
        ("Read Book", "Read a book for 1 hour", "daily", "13:00", "daily"),
        ("Weekly Meditation", "Meditate for 2 hours every weekend", "weekly", "10:30", "weekly"),
        ("Guitar Practice", "Practice playing the guitar for 1 hour", "daily", None, None),
        ("Learn 50 Words in Thai", "Learn 50 words from a foreign language.", "monthly", None, None)
    ]
    
    with with_database_connection() as cursor:
        for habit_name, description, periodicity, next_reminder_time, reminder_frequency in habits_and_reminders:
            # Insert the habit into the Database
            cursor.execute("INSERT INTO habits (username, title, description, periodicity, creation_date) VALUES (?, ?, ?, ?, ?)", 
                           (username, habit_name, description, periodicity, datetime.datetime.now()))
            
            # Fetch the ID of the habit just inserted
            habit_id = cursor.lastrowid
            
            # Insert the reminder if it exists
            if next_reminder_time:
                cursor.execute("INSERT INTO reminders (habit_id, next_reminder_time, reminder_frequency) VALUES (?, ?, ?)", 
                               (habit_id, next_reminder_time, reminder_frequency))
                

def mark_habit_complete_for_teeLv(habit_id, completion_date=None, reward_system=None):
    mark_habit_complete(habit_id, completion_date)
    if reward_system:
        # habit is always completed successfully so reward function is called
        reward_system.reward_for_habit_completion(None)  
        

def populate_database_for_teeLv():
    # Database connection
    with with_database_connection() as cursor:
        # Retrieve habit_ids for user "TeeLv"
        cursor.execute("SELECT id FROM habits WHERE username=?", ("TeeLv",))
        habit_ids = [row[0] for row in cursor.fetchall()]

        # Habit #1 ("Morning Run"): Daily completion from 2023-07-25 to 2023-08-22
        start_date = datetime.date(2023, 7, 25)  # Reset the start_date
        end_date = datetime.date(2023, 8, 22)
        while start_date <= end_date:
            mark_habit_complete_for_teeLv(habit_ids[0], start_date)
            start_date += datetime.timedelta(days=1)

        # Habit #2 ("Read Book"): 12 random completions in the date range
        start_date = datetime.date(2023, 7, 25)  # Reset the start_date
        random_dates = random.sample([start_date + datetime.timedelta(days=i) for i in range((end_date-start_date).days + 1)], 12)
        for date in random_dates:
            mark_habit_complete_for_teeLv(habit_ids[1], date)

        # Habit #3 ("Weekly Meditation"): Every 7 days in the date range
        start_date = datetime.date(2023, 7, 25)  # Reset the start_date
        while start_date <= end_date:
            mark_habit_complete_for_teeLv(habit_ids[2], start_date)
            start_date += datetime.timedelta(days=7)

        # Habit #4 ("Guitar Practice"): 20 random completions in the date range
        start_date = datetime.date(2023, 7, 25)  # Reset the start_date
        random_dates = random.sample([start_date + datetime.timedelta(days=i) for i in range((end_date-start_date).days + 1)], 20)
        for date in random_dates:
            mark_habit_complete_for_teeLv(habit_ids[3], date)
        
        # Habit #5 ("Learn 50 Words in Thai"): completed on 2023-08-08
        mark_habit_complete_for_teeLv(habit_ids[4], datetime.date(2023, 8, 8))

if __name__ == "__main__":
    # Create an instance of the User class and attempt to log in
    user_instance = User("TeeLv", "12")
    
    if user_instance.login():
        print("Login successful!")
        
        # Initialize the Reward system for the logged-in user
        user_reward_system = Reward("TeeLv")
        
        populate_TeeLv_habits_and_reminders("TeeLv")
        populate_database_for_teeLv()

        with with_database_connection() as cursor:
            # Fetch all habit completions for TeeLv
            cursor.execute("""SELECT habits.id, completions.completion_date FROM habits
                              JOIN completions ON habits.id = completions.habit_id
                              WHERE habits.username = ?""", ("TeeLv",))
            
            habit_completions = cursor.fetchall()
            
            for habit_id, completion_date in habit_completions:
                mark_habit_complete_for_teeLv(habit_id, completion_date, user_reward_system)
        
        print("Successfully populated!")
    else:
        print("Login failed!")