from sqlite3 import OperationalError
from datetime import datetime, timedelta
from database_operations import with_database_connection
from habit_operations import add_habit, get_habits, mark_habit_complete, delete_habit, habit_exists_for_user
from user_operations import register_user, verify_user


# The 'User' class represents a user of the Habit Tracker application.
class User:
    def __init__(self, username, password, user_id=None):
        # Initialize user properties: username, password, user ID
        self.username = username
        self.password = password
        self.user_id = user_id
        self.reward = Reward(username)  # Initialize a reward instance for the user.
        
    def get_user_id(self):
        # Get the user's ID.
        return self.user_id

    def register(self):
        # Register the user by calling the 'register_user' function with the user's credentials.
        return register_user(self.username, self.password)

    def login(self):
        # Log in the user by verifying their credentials and initializing habits, rewards and a check for broken streaks
        is_verified = verify_user(self.username, self.password)
        if is_verified:
            self.reward = Reward(self.username)  # Initialize the user's reward instance.
            self.reward.points_manager = Reward(self.username)  # Set up reward points manager.
            
            # Fetch user's habits, populate completion dates, and check for broken streaks.
            habits = get_habits(self.username, self)
            for habit in habits:
                habit.populate_completion_dates()
                habit.breakStreak()
        return is_verified
    
    def _setup_user_rewards_and_habits(self):
        # Set up the user's rewards and habits
        self._reward = Reward(self.username)
        habits = get_habits(self.username, self)
        for habit in habits:
            habit.populate_completion_dates()
            

    def habit_exists(self, title):
        # Check if a habit with the given title exists for the user.
        return habit_exists_for_user(self.username, title)

    def addHabit(self, title, description, periodicity):
        # Add a new habit for the user, if it doesn't already exist.
        if self.habit_exists(title):
            print(f"The habit titled '{title}' already exists!")
        else:
            add_habit(self.username, title, description, periodicity)
    
    def removeHabit(self, title):
        # Remove a habit with the given title from the user's account.
        delete_habit(self.username, title)

    def getHabits(self):
        # Get a list of habits associated with the user.
        return get_habits(self.username, self)
    
    def get_reward(self):
        # Add 10 points to the user's reward points.
        self.reward.add_points(10)
        
    def get_habit_by_title(self, title):
        # Fetch the user's habits
        habits = self.getHabits()

        # Search through the habits for the specified title
        for habit in habits:
            if habit.title == title:
                return habit
        return None


# The 'SessionManager' class is responsible for managing active user sessions within the Habit Tracker application.
class SessionManager:
    def __init__(self):
        # Initialize an empty dictionary to store active user sessions.
        self.active_sessions = {}

    def start_session(self, user):
        # Start a session for the provided user by associating their user ID with the user object.
        user_id = user.get_user_id()
        self.active_sessions[user_id] = user

    def end_session(self, user):
        # End the session for the provided user by removing their user ID from the active sessions.
        user_id = user.get_user_id()
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]

    def get_active_user(self, user_id):
        # Get the active user associated with the provided user ID from the active sessions.
        return self.active_sessions.get(user_id)

        
# The 'Habit' class represents a habit in the Habit Tracker application.
class Habit:
    def __init__(self, habit_id, title, description, periodicity, user, reminder_time=None, streak_broken_date=None):
        # Initialize habit properties: habit ID, title, description, periodicity, creation date,
        # completion dates, user, optional reminder time, and streak_broken_date.
        self.habit_id = habit_id
        self.title = title
        self.description = description
        self.periodicity = periodicity
        self.creation_date = datetime.now()
        self.completion_dates = []
        self.user = user
        self.reminder_time = reminder_time  # Optional reminder time property.
        self.streak_broken_date = streak_broken_date  # Streak broken date
        
    
    def save(self):
        # Save or update the habit's details in the database.
        with with_database_connection() as cursor:
            if self.habit_id is None:
                # Insert a new habit record if it doesn't have an ID.
                cursor.execute(
                    "INSERT INTO habits (username, title, description, periodicity, creation_date) VALUES (?, ?, ?, ?, datetime('now'))",
                    (self.user, self.title, self.description, self.periodicity)
                )
                self.habit_id = cursor.lastrowid
            else:
                # Update an existing habit's details.
                cursor.execute(
                    "UPDATE habits SET title = ?, description = ?, periodicity = ? WHERE id = ?",
                    (self.title, self.description, self.periodicity, self.habit_id)
                )
    
    def edit(self, new_title=None, new_description=None, new_periodicity=None):
        """Edit habit details"""
        # Edit habit details by updating properties if new values are provided.
        if new_title:
            self.title = new_title
        if new_description:
            self.description = new_description
        if new_periodicity:
            self.periodicity = new_periodicity

    def __str__(self):
        # Return a string representation of the habit in the format "Title - Description".
        return f"{self.title} - {self.description}"

    
    def getStreak(self):
        # Calculate and return the streak of completed days for the habit.
        with with_database_connection() as cursor:
            # Retrieve completion dates for the habit from the database.
            cursor.execute("SELECT DISTINCT date(completion_date) FROM completions WHERE habit_id=?", (self.habit_id,))
            completion_dates = [datetime.strptime(date[0], '%Y-%m-%d').date() for date in cursor.fetchall()]

            # If there are no completion dates, the streak is zero.
            if not completion_dates:
                return 0

            # Sort completion dates in descending order and get today's date.
            sorted_dates = sorted(completion_dates, reverse=True)
            today = datetime.today().date()

            # Determine the time period based on the habit's periodicity.
            if self.periodicity == "daily":
                delta = timedelta(days=1)
            elif self.periodicity == "weekly":
                delta = timedelta(weeks=1)
            elif self.periodicity == "monthly":
                delta = timedelta(days=30)
            else:
                raise ValueError(f"Unsupported periodicity: {self.periodicity}")
            
            streak = 1  # Initialize streak counter.
            # Calculate the streak by comparing completion dates.
            for i in range(len(sorted_dates) - 1):
                date_difference = sorted_dates[i] - sorted_dates[i + 1]
                if date_difference == delta:
                    streak += 1
                elif date_difference > delta:
                    break  # If the streak is broken, stop counting.
            return streak  # Return the calculated streak.

    
    def populate_completion_dates(self):
        # Retrieve and populate completion dates for the habit from the database.
        with with_database_connection() as cursor:
            cursor.execute("SELECT completion_date FROM completions WHERE habit_id=?", (self.habit_id,))
            # Convert completion dates to datetime objects and store in the habit's completion_dates list.
            self.completion_dates = [datetime.strptime(date[0], '%Y-%m-%d').date() for date in cursor.fetchall()]

            
    def markComplete(self):
        # Mark the habit as complete and perform related actions.
        with with_database_connection() as cursor:
            # Insert a new completion record into the database.
            cursor.execute("INSERT INTO completions (habit_id, completion_date) VALUES (?, datetime('now'))", (self.habit_id,))
            # Add points to the user's reward and notify completion.
            self.user.add_points(10)
            print("Habit completed! +10 points")
            # Trigger the reward system for the habit completion.
            self.user.reward.reward_for_habit_completion(self)

    
    def breakStreak(self):
        latest_completion = max(self.completion_dates)
        today = datetime.today().date()

        # Determine the time period based on the habit's periodicity.
        if self.periodicity == "daily":
            delta = timedelta(days=1)
        elif self.periodicity == "weekly":
            delta = timedelta(days=7)
        elif self.periodicity == "monthly":
            delta = timedelta(days=30)
        else:
            raise ValueError(f"Unsupported periodicity: {self.periodicity}")

        # Check if the streak was already marked broken for today.
        today_date = datetime.today().date()
        if self.streak_broken_date:
            if isinstance(self.streak_broken_date, str):
                try:
                    # Try parsing as full timestamp
                    streak_broken_datetime = datetime.strptime(self.streak_broken_date, "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    # Fall back to date-only format
                    streak_broken_datetime = datetime.strptime(self.streak_broken_date, "%Y-%m-%d")
            elif isinstance(self.streak_broken_date, datetime):
                streak_broken_datetime = self.streak_broken_date
            else:
                raise TypeError("Unexpected type for streak_broken_date")

            if streak_broken_datetime.date() == today_date:
                return

        # Check if the streak is broken.
        if (today - latest_completion) > delta:
            # Update the streak broken date in the database and the Habit instance.
            now = datetime.now()
            with with_database_connection() as cursor:
                cursor.execute("UPDATE habits SET streak_broken_date = ? WHERE id = ?", (now, self.habit_id))
            self.streak_broken_date = now

            # Deduct points for breaking the streak.
            self.user.reward.add_points(-10)
            print("Streak broken! -10 points")
                
            
    def delete_habit_by_id(self, habit_id):
        # Delete a habit from the database by its ID.
        with with_database_connection() as cursor:
            cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))

    
    
# The 'Reminder' class represents a reminder for a specific habit
class Reminder:
    def __init__(self, habit=None, nextReminderTime=None, reminderFrequency=None):
        # Initialize reminder properties: associated habit, next reminder time, and reminder frequency.
        self.habit = habit
        self.nextReminderTime = nextReminderTime
        self.reminderFrequency = reminderFrequency

    @classmethod
    def get_reminders_for_habit(cls, habit_id):
        # Retrieve reminder time for a habit from the database based on its ID.
        with with_database_connection() as cursor:
            cursor.execute("SELECT next_reminder_time FROM reminders WHERE id=?", (habit_id,))
            result = cursor.fetchall()
            return result[0] if result else None

    def resetReminder(self):
        # Reset the reminder's next reminder time based on its frequency.
        self.nextReminderTime += timedelta(days=self.reminderFrequency)
        
    @staticmethod
    def add_reminder(habit_id, next_reminder_time, reminder_frequency):
        # Add a reminder to the database for a specific habit.
        with with_database_connection() as cursor:
            cursor.execute(
                "INSERT INTO reminders (habit_id, next_reminder_time, reminder_frequency) VALUES (?, ?, ?)",
                (habit_id, next_reminder_time, reminder_frequency)
            )

# The 'Analytics' class provides methods to analyze and retrieve insights from the user's habits
class Analytics:
    def __init__(self, habits):
        # Initialize the class with a list of user habits for analysis.
        self.habits = habits

    def getAllHabits(self):
        # Return a list of all user habits for analysis.
        return self.habits

    def getHabitsByPeriodicity(self, periodicity):
        # Return a list of user habits filtered by the specified periodicity.
        return [habit for habit in self.habits if habit.periodicity == periodicity]

    def getLongestStreakAllHabits(self):
        # Retrieve the longest streak across all user habits.
        with with_database_connection() as cursor:
            return max([habit.getStreak() for habit in self.habits], default=0)

    def getLongestStreakForHabit(self, user, habit_title):
        """
        Get the longest streak for a specific habit of the user.

        Parameters:
        - user (User): The user object.
        - habit_title (str): The title of the habit for which to get the longest streak.

        Returns:
        - int: The longest streak for the habit.
        """
        # Get the habit object based on the habit title.
        habit = user.get_habit_by_title(habit_title)
        if habit:
            return habit.getStreak()
        else:
            print(f"Habit with title '{habit_title}' not found for user '{user.username}'.")
            return None

    def get_user_points(self, user):
        # Retrieve the points accumulated by the user's reward system.
        return user.reward.points_manager.points
    
    
    
# The 'Reward' class manages the user's reward system in the Habit Tracker application.
class Reward:
    def __init__(self, username):
        # Initialize the reward system for a specific user.
        self.username = username
        self.points = self.get_points()  # Retrieve the user's current points from the database.

    def add_points(self, points_to_add):
        # Add points to the user's reward balance and update the database.
        self.points += points_to_add
        self.update_points_in_db(points_to_add)

    def reward_for_habit_completion(self, habit):
        # Reward the user with points for completing a habit.
        self.add_points(10)

    def update_points_in_db(self, points_to_add):
        # Update the user's points in the database.
        with with_database_connection() as cursor:
            cursor.execute("UPDATE users SET points = points + ? WHERE username = ?", (points_to_add, self.username))

    def get_points(self):
        # Retrieve the user's current points from the database.
        try:
            with with_database_connection() as cursor:
                cursor.execute("SELECT points FROM users WHERE username = ?", (self.username,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return 0
        except OperationalError as e:
            print(f"Error accessing database: {e}")
            return 0