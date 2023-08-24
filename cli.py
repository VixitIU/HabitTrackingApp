from models import User, SessionManager, Habit, Analytics, Reminder, Reward
from database_operations import with_database_connection, setup_database
from datetime import time
from habit_operations import add_habit, get_habits, mark_habit_complete, delete_habit 
from user_operations import register_user, verify_user


# Create an instance of the SessionManager class to manage user sessions.
session_manager = SessionManager()

# The main function for the Habit Tracker CLI.
def main_cli():
    setup_database()
    # Initialize variables for the active user and analytics.
    active_user = None
    analytics = None

    # Enter the main CLI loop.
    while True:
        # If there is no active user, show registration, login, and quit options.
        if not active_user:
            print("Habit Tracker CLI:")
            print("1. Register\n2. Login\n3. Quit")
            choice = input("Enter your choice: ")

            # Handle user registration.
            if choice == "1":
                username = input("Enter a username: ")
                password = input("Enter a password: ")
                user = User(username, password)

                if user.register():
                    active_user = user
                    session_manager.start_session(user)
                    print("Successfully registered and logged in!")
                else:
                    print("Registration failed!")

            # Handle user login.
            elif choice == "2":
                username = input("Enter a username: ")
                password = input("Enter a password: ")
                user = User(username, password)
                if user.login():
                    active_user = user
                    print("Successfully logged in!")
                else:
                    print("Login failed!")
                    continue

            # Quit the CLI loop and exit the program.
            elif choice == "3":
                print("Goodbye!")
                break
                
        else:
            # Display options for logged-in users: Add Habit, View Habits, Mark Habit as Complete, Check Rewards, View Analytics, Logout
            print("1. Add Habit\n2. View Habits\n3. Mark Habit as Complete\n4. Check Rewards\n5. View Analytics\n6. Logout")
            choice = input("Enter your choice: ")
            
            # Handle adding a new habit.
            if choice == "1":
                title = input("Enter habit title: ")
                description = input("Enter habit description: ")
                periodicity = input("Enter periodicity (daily/weekly/monthly): ")

                reminder_obj = None
                want_reminder = input("Do you want to set a reminder for this habit? (yes/no): ")
                if want_reminder.lower() == "yes":
                    hour = int(input("Enter hour (0-23): "))
                    minute = int(input("Enter minute (0-59): "))
                    next_reminder_time = f"{hour:02d}:{minute:02d}" 
                    reminder_frequency = input("Enter periodicity (daily/weekly/monthly): ")
                    reminder_obj = Reminder(None, next_reminder_time, reminder_frequency)

                add_habit(active_user.username, title, description, periodicity, reminder_obj)
                    
            # Handle viewing existing habits.
            elif choice == "2":
                with with_database_connection() as cursor:
                    habits = get_habits(active_user.username, active_user)

                if habits:
                    for idx, habit in enumerate(habits, 1):
                        print(f"{idx}. {habit.title} ({habit.description})")

                    delete_choice = input("Do you want to delete a habit? (yes/no): ").lower()

                    if delete_choice == 'yes':
                        try:
                            habit_choice = int(input("Select habit number to delete: "))
                            if 1 <= habit_choice <= len(habits):
                                selected_habit = habits[habit_choice - 1]
                                confirmation = input(f"Are you sure you want to delete the habit '{selected_habit.title}'? (yes/no): ").lower()
                                if confirmation == 'yes':
                                    delete_habit(active_user.username, selected_habit.title)
                                    print(f"Habit '{selected_habit.title}' has been deleted.")
                                else:
                                    print("Habit not deleted.")
                            else:
                                print("Invalid choice. Please select a number from the given list.")
                        except ValueError:
                            print("Please enter a valid number.")
                else:
                    print("No habits found!")

                        
                        
            elif choice == "3":
                # Establish a connection to the database.
                with with_database_connection() as cursor:
                    # Retrieve the list of habits associated with the currently active user.
                    habits = get_habits(active_user.username, active_user)

                # Check if there are habits to display.
                if habits:
                    # Loop through the list of habits and display each one with its index.
                    for idx, habit in enumerate(habits, 1):
                        print(f"{idx}. {habit.title} ({habit.description})")

                    try:
                        # Prompt the user to select a habit from the displayed list by entering its index.
                        habit_choice = int(input("Select habit number to mark as complete: "))

                        # Check if the entered index is within the valid range.
                        if 1 <= habit_choice <= len(habits):
                            # Get the habit corresponding to the chosen index.
                            selected_habit = habits[habit_choice - 1]

                            # Ask the user if they want to specify a custom date for habit completion.
                            use_custom_date = input("Do you want to provide a completion date? (yes/no): ").lower()
                            if use_custom_date == 'yes':
                                # Prompt the user to enter the date of completion.
                                completion_date = input("Enter the completion date in YYYY-MM-DD format: ")
                            else:
                                # If no custom date is provided, set the completion date to None (current date will be used).
                                completion_date = None

                            # Mark the selected habit as complete and store the completion date.
                            mark_habit_complete(selected_habit.habit_id, completion_date)

                            # Check if the user's reward system is initialized.
                            if active_user and active_user.reward:
                                # Provide reward points to the user for completing the habit.
                                active_user.reward.reward_for_habit_completion(selected_habit)
                                # Display the updated reward points.
                                print(f"After marking habit as complete, points are: {active_user.reward.points}")
                            else:
                                # Inform the user if there's an issue with their reward system.
                                print("Error: The user or the user's reward system is not properly initialized.")
                        else:
                            # Inform the user if their choice is not valid.
                            print("Invalid choice. Please select a number from the given list.")
                    except ValueError:
                        # Handle the exception if the user enters a non-numeric value.
                        print("Please enter a valid number.")
                else:
                    # Inform the user if they have no habits to mark as complete.
                    print("No habits to mark!")

                    
            elif choice == "4":
                # Display the user's points.
                reward = Reward(active_user.username)
                analytics = Analytics(active_user.username)
                if analytics:
                    print(f"You have these many points: {reward.points}") 
                else:
                    print("No other rewards so far.")

            elif choice == "5":
                # Retrieve the user's habits and create an Analytics object.
                habits_objects = get_habits(active_user.username, active_user)
                analytics = Analytics(habits_objects)

                # Display various analytics related to the user's habits.
                print(f"Total habits: {len(analytics.getAllHabits())}")
                habit_list = [str(habit) for habit in analytics.getAllHabits()]
                print(f"Your habit list: {habit_list}")
                print(f"Daily habits count: {len(analytics.getHabitsByPeriodicity('daily'))}")
                print(f"Weekly habits count: {len(analytics.getHabitsByPeriodicity('weekly'))}")
                print(f"Monthly habits count: {len(analytics.getHabitsByPeriodicity('monthly'))}")
                print(f"Longest streak across all habits: {analytics.getLongestStreakAllHabits()}")

                # New functionality to get the longest streak for a specific habit.
                specific_habit_query = input("Do you want to get the longest streak for a specific habit? (yes/no): ").lower()

                if specific_habit_query == 'yes':
                    habit_title = input("Enter the title of the habit you're interested in: ")
                    longest_streak = analytics.getLongestStreakForHabit(active_user, habit_title)

                    if longest_streak is not None:
                        print(f"The longest streak for habit '{habit_title}' is {longest_streak} days.")
                    else:
                        print(f"Unable to retrieve the longest streak for habit '{habit_title}'.")
                    
            elif choice == "6":
                # Log out the active user.
                active_user = None 
                print("Logged out successfully!")
                
if __name__ == "__main__":
    main_cli()
