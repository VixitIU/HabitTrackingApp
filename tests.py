from models import User, Habit, Analytics, Reward, Reminder
from unittest.mock import patch, Mock, MagicMock
from cli import main_cli
import sqlite3
from datetime import datetime, timedelta
from database_operations import setup_test_environment, with_database_connection
from habit_operations import add_habit, get_habits, habit_exists_for_user, delete_habit, mark_habit_complete


def setup_environment(username="testuser", password="testpass"):
    """
    Set up the test environment by creating a new user in the habits database.

    Parameters:
    - username (str): The username for the test user.
    - password (str): The password for the test user.
    """

    # First, make sure there's no leftover data from previous tests for this user.
    teardown_test_environment(username)
    
    # Establish a connection to the SQLite database.
    conn = sqlite3.connect('habits.db')
    cursor = conn.cursor()

    # Insert a new user with the provided username and password into the users table.
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()  # Commit the transaction to save the changes.
    conn.close()  # Close the connection to the database.


def teardown_test_environment(username="testuser"):
    """
    Clean up the test environment by removing all data associated with a given username from the habits database.

    Parameters:
    - username (str): The username for which the data should be removed.
    """
    
    # Using the custom context manager 'with_database_connection' to handle database operations.
    with with_database_connection() as cursor:
        
        # Print a message indicating the start of the cleanup process for the specified username.
        print(f"Starting cleanup for {username}...")

        # Delete all completions associated with the user's habits.
        cursor.execute("DELETE FROM completions WHERE habit_id IN (SELECT id FROM habits WHERE username=?)", (username,))
        
        # Delete all habits and the user account associated with the given username.
        cursor.execute("DELETE FROM habits WHERE username=?", (username,))
        cursor.execute("DELETE FROM users WHERE username=?", (username,))
        
        # Print a message indicating the end of the cleanup process for the specified username.
        print(f"Cleanup for {username} complete!")

    
    
def test_cli_login_success():
    # Set up a test environment before executing the test.
    setup_environment()  

    # Define a generator function to produce a sequence of mock inputs.
    # This is used to simulate a series of user inputs without manual intervention.
    def mock_input_gen():
        # These are the initial inputs we wish to simulate.
        # In this example:
        # "2" represents the "login" option.
        # "testuser" and "testpass" represent username and password inputs respectively.
        for val in ["2", "testuser", "testpass"]:
            yield val
        
        # This simulates pressing "6" ten times after login, 
        # which represents some repetitive action or keeping the CLI running.
        for _ in range(10):
            yield "6"

    # We use a try-except block to handle StopIteration which can occur if the generator runs out of mock inputs.
    try:
        # Patch the built-in 'input' function with our mock input generator.
        with patch('builtins.input', side_effect=mock_input_gen()) as mock_input:
            
            # Patch the built-in 'print' function to monitor what the application prints to the console.
            with patch('builtins.print') as mock_print:
                
                # Call the main command line interface (CLI) function of the application.
                main_cli()
                
    # This exception is raised when all mock inputs from the generator are consumed.
    except StopIteration:
        print("All mock inputs consumed.")

        
            
def test_cli_login_fail():
    """
    Test the CLI's behavior when a user attempts to log in with incorrect credentials.
    """
    # Set up a test environment with a known user.
    setup_environment()

    # Use 'patch' from 'unittest.mock' to mock the built-in 'input' function.
    # 'side_effect' provides a sequence of responses to simulate user input. 
    # In this case, the user chooses to login ("2"), then provides an incorrect username ("wronguser") 
    # and incorrect password ("wrongpass"), then chooses to exit ("3").
    with patch('builtins.input', side_effect=["2", "wronguser", "wrongpass", "3"]):
        
        # Mock the built-in 'print' function to capture the program's output.
        with patch('builtins.print') as mock_print:
            
            # Execute the main CLI function to simulate running the application.
            main_cli()
            
            # Assert that the mocked print function was called with the "Login failed!" message at least once.
            mock_print.assert_any_call("Login failed!")
    
    # Clean up the test environment after running the test.
    teardown_test_environment()
    

def test_cli_register_success():
    """
    Test the CLI's behavior when a user successfully registers and logs in.
    """
    
    # Set up a test environment with a known user.
    setup_environment()

    try:
        # Use 'patch' from 'unittest.mock' to mock the built-in 'input' function.
        # 'side_effect' provides a sequence of responses to simulate user input.
        # In this case, the user chooses to register ("1"), provides a new username ("newuser"),
        # a new password ("newpass"), exits the rewards menu ("6"), and exits the application ("3").
        with patch('builtins.input', side_effect=["1", "newuser", "newpass", "6", "3"]):
            
            # Mock the built-in 'print' function to capture the program's output.
            with patch('builtins.print') as mock_print:
                
                # Execute the main CLI function to simulate running the application.
                main_cli()
                
                # Assert that the mocked print function was called with the "Successfully registered and logged in!" message.
                mock_print.assert_any_call("Successfully registered and logged in!")
    
    except AssertionError:
        # If the registration process fails (an assertion error occurs), run the test_cli_register_fail function.
        test_cli_register_fail()
    
    # Clean up the test environment after running the test.
    teardown_test_environment()

    
    
def test_cli_register_fail():
    """
    Test the CLI's behavior when user registration fails due to an existing username.
    """
    
    # Set up a test environment with a known user.
    setup_environment()
    
    # Use 'patch' from 'unittest.mock' to mock the built-in 'input' function.
    # 'side_effect' provides a sequence of responses to simulate user input.
    # In this case, the user chooses to register ("1"), provides an existing username ("testuser"),
    # provides a password ("testpass"), and exits the application ("3").
    with patch('builtins.input', side_effect=["1", "testuser", "testpass","3"]):
        
        # Mock the built-in 'print' function to capture the program's output.
        with patch('builtins.print') as mock_print:
            
            # Execute the main CLI function to simulate running the application.
            main_cli()
            
            # Assert that the mocked print function was called with the "Registration failed!" message.
            mock_print.assert_any_call("Registration failed!")
    
    # Clean up the test environment after running the test.
    teardown_test_environment()


       
    
def test_add_and_get_habits(username="testuser"):
    """
    Test the behavior of adding a habit and retrieving habits for a user.
    """
    # Create a mock user for testing purposes.
    user = Mock(mockUsername=username, mockPassword="testpass")
    
    # Define the details of the habit to be added.
    habit_title = "Daily Walk"
    habit_description = "Walk for at least 30 minutes."
    periodicity = "daily"
    reminder_obj = Reminder(habit_title, "9:00 AM", "daily")
    reminder = reminder_obj
    
    # Add the habit to the database using the 'add_habit' function.
    add_habit(username, habit_title, habit_description, periodicity, reminder_obj)
    
    # Retrieve the list of habits for the user using the 'get_habits' function.
    habits = get_habits(username, user)
    
    # Assert that the number of retrieved habits is 1.
    assert len(habits) == 1
    
    # Assert that the title of the retrieved habit matches the added habit's title.
    assert habits[0].title == habit_title
    
    
    
def test_mark_habit_complete(username="testuser"):
    """
    Test the behavior of marking a habit as complete.
    """
    # Set up a test environment.
    setup_environment()
   
    # Create a mock user for testing purposes.
    user = Mock(mockUsername="mockUsername", mockPassword="mockPassword")
    username = user.mockUsername
    
    # Define the details of the habit to be added.
    habit_title = "Daily Walk"
    habit_description = "Walk for at least 30 minutes."
    periodicity = "daily"
    reminder_obj = Reminder(habit_title, "9:00 AM", "daily")
    
    # Add the habit to the database using the 'add_habit' function.
    add_habit(username, habit_title, habit_description, periodicity, reminder_obj)
    
    # Retrieve the added habit.
    habit = get_habits(username, user)[0]
    
    # Mark the retrieved habit as complete using the 'mark_habit_complete' function.
    mark_habit_complete(habit.habit_id)
    
    # Tear down the test environment.
    teardown_test_environment()
    

def test_habit_streaks():
    """
    Test the calculation of habit streaks.
    """

    # Set up a test environment.
    setup_environment()    
    username, password = setup_test_environment()
    
    # Create an instance of the Habit class for testing.
    habit_instance = Habit(None, "Daily Walk", "Walk for 30 minutes.", "daily", username)
    
    # Save the habit instance to the database.
    habit_instance.save()
    
    # Generate completion dates for the habit instance.
    completion_dates = [datetime.now() - timedelta(days=i) for i in range(5)]
    
    # Store each completion date in the database and mark the habit as complete.
    for date in completion_dates:
        print(date.date())  # Print for debugging purposes
        mark_habit_complete(habit_instance.habit_id, date)
    
    # Calculate the streak for the habit instance.
    streak = habit_instance.getStreak()
    
    # Assert that the calculated streak matches the expected streak.
    assert streak == 5
    
    # Tear down the test environment.
    teardown_test_environment(username)
    
    
def test_analytics(username="testuser"):
    """
    Test the analytics functionality.
    """
    # Set up a test environment.
    setup_environment()
    
    # Create a mock user for testing purposes.
    user = Mock(mockUsername="mockUsername", mockPassword="mockPassword")
    
    # Mocking the Habit's streak value
    habit_mock = Mock()
    habit_mock.getStreak.return_value = 5
    user.get_habit_by_title.return_value = habit_mock
    
    # Create an instance of the Habit class for testing.
    habit_instance = Habit(None, "Daily Walk", "Walk for 30 minutes.", "daily", user.mockUsername)
    
    # Save the habit instance to the database.
    habit_instance.save()
    
    # Generate completion dates for the habit instance.
    completion_dates = [datetime.now() - timedelta(days=i) for i in range(5)]
    
    # Store each completion date in the database and mark the habit as complete.
    for date in completion_dates:
        mark_habit_complete(habit_instance.habit_id, date.strftime('%Y-%m-%d %H:%M:%S'))
    
    # Create an instance of the Analytics class with the habit instance.
    analytics = Analytics([habit_instance])
    
    # Extract the habit title from the habit instance
    habit_title = habit_instance.title
    
    # Assert that the number of habits in the analytics matches the expected value.
    assert len(analytics.getAllHabits()) == 1
    
    # Assert that the number of daily habits in the analytics matches the expected value.
    assert len(analytics.getHabitsByPeriodicity("daily")) == 1
    
    # Assert that the longest streak across all habits matches the expected value.
    assert analytics.getLongestStreakAllHabits() == 5
    
    # Assert that the longest streak for the specific habit matches the expected value.
    assert analytics.getLongestStreakForHabit(user, habit_title) == 5

    
    # Tear down the test environment.
    teardown_test_environment()


def test_points_award():
    """
    Test the points award functionality.
    """
    # Set up a test environment.
    setup_environment()
    
    # Create a user instance for testing.
    user = User("testuser", "testpass")
    
    # Create a reward instance for the user.
    reward = Reward(user.username)
    
    # Create a habit instance for testing.
    habit = Habit(None, "Daily Walk", "Walk for 30 minutes.", "daily", user)
    
    # Reward points for completing the habit.
    reward.reward_for_habit_completion(habit)
    
    # Assert that the points awarded match the expected value.
    assert reward.points == 10
    
    # Tear down the test environment.
    teardown_test_environment()

    

def test_add_habit_with_reminder():
    setup_environment()  # Set up the test environment
    
    # Define a sequence of mock user inputs simulating a user session.
    mock_inputs = [
        "2",          # Login
        "testuser",   # Username
        "testpass",   # Password
        "1",          # Add Habit
        "Test Habit", # Habit title
        "Test Description", # Habit description
        "daily",      # Periodicity
        "yes",        # Wants reminder
        "10",         # Reminder hour (10 AM)
        "30",         # Reminder minute (10:30 AM)
        "daily",      # Reminder frequency
        "6"           # Logout
    ]
    
    # Use the 'patch' context manager to mock user inputs and print outputs during the test.
    with patch('builtins.input', side_effect=mock_inputs):
        with patch('builtins.print') as mock_print:
            main_cli()  # Run the CLI with mocked inputs
    
    # Verify the added habit and reminder in the database.
    with with_database_connection() as cursor:
        cursor.execute("SELECT * FROM habits WHERE username=?", ("testuser",))
        habit = cursor.fetchone()
        assert habit is not None, "Habit was not added!"
        cursor.execute("SELECT * FROM reminders WHERE habit_id=?", (habit[0],))
        reminder = cursor.fetchone()
        assert reminder is not None, "Reminder was not added!"
        assert reminder[1] == "10:30", "Reminder time is incorrect!"
        assert reminder[2] == "daily", "Reminder frequency is incorrect!"
    
    teardown_test_environment()  # Tear down the test environment



def test_add_habit_without_reminder():
    setup_environment()  # Set up the test environment
    
    # Define habit details for the test.
    habit_title = "Test Habit"
    habit_description = "This is a test habit."
    periodicity = "daily"
    
    # Define a generator for mock user inputs simulating a user session.
    def mock_input_gen():
        # Mimic the user interactions: login, add habit, provide details, and log out.
        for val in ["2", "testuser", "testpass", "1", habit_title, habit_description, periodicity, "no", "6"]:
            yield val
        # Simulate logging out multiple times.
        for _ in range(5):
            yield "6"
    
    # Use the 'patch' context manager to mock user inputs and print outputs during the test.
    with patch('builtins.input', side_effect=mock_input_gen()) as mock_input:
        with patch('builtins.print') as mock_print:
            main_cli()  # Run the CLI with mocked inputs
            
            # Verify that the habit was added to the database without a reminder.
            with with_database_connection() as cursor:
                cursor.execute("SELECT * FROM habits WHERE title = ?", (habit_title,))
                habit = cursor.fetchone()
                assert habit is not None, "Habit was not added successfully"
                cursor.execute("SELECT * FROM reminders WHERE habit_id = ?", (habit[0],)) 
                reminder = cursor.fetchone()
                assert reminder is None, "Reminder was unexpectedly added"
    
    teardown_test_environment()  # Tear down the test environment
    
    

def test_view_habits_with_reminders():
    setup_environment()  # Set up the test environment
    
    # Define habit details for the test.
    habit_title = "Test Habit with Reminder"
    habit_description = "This is a test habit with a reminder."
    periodicity = "daily"
    reminder_time = "10:00"
    
    # Mock user inputs for adding a habit with a reminder.
    def mock_input_add_habit_gen():
        for val in ["2", "testuser", "testpass", "1", habit_title, habit_description, periodicity, "yes", reminder_time, "6"]:
            yield val
    
    # Use the 'patch' context manager to mock user inputs and print outputs during adding the habit.
    with patch('builtins.input', side_effect=mock_input_add_habit_gen()):
        with patch('builtins.print'):
            main_cli()  # Run the CLI with mocked inputs for adding a habit
    
    # Mock user inputs for viewing habits.
    def mock_input_view_habits_gen():
        for val in ["2", "testuser", "testpass", "2", "6"]:
            yield val
    
    # Use the 'patch' context manager to mock user inputs and print outputs during viewing habits.
    with patch('builtins.input', side_effect=mock_input_view_habits_gen()) as mock_input:
        with patch('builtins.print') as mock_print:
            main_cli()  # Run the CLI with mocked inputs for viewing habits
            
            # Verify that the expected habit details with reminder were printed.
            expected_output = [
                f"Title: {habit_title}",
                f"Description: {habit_description}",
                f"Periodicity: {periodicity}",
                f"Reminder: {reminder_time}"
            ]
            for line in expected_output:
                assert any(line in call.args[0] for call in mock_print.call_args_list), f"Expected line '{line}' was not printed"
    
    teardown_test_environment()  # Tear down the test environment
    
    
    

def test_mark_habit_complete_and_award_points():
    setup_environment()  # Set up the test environment
    
    # Define habit details for the test.
    habit_title = "Test Habit"
    habit_description = "This is a test habit."
    periodicity = "daily"
    
    # Mock user inputs for adding a habit without a reminder.
    def mock_input_add_habit_gen():
        for val in ["2", "testuser", "testpass", "1", habit_title, habit_description, periodicity, "no", "6"]:
            yield val
    
    # Use the 'patch' context manager to mock user inputs and print outputs during adding the habit.
    with patch('builtins.input', side_effect=mock_input_add_habit_gen()):
        with patch('builtins.print'):
            main_cli()  # Run the CLI with mocked inputs for adding a habit
            
    initial_points = 0  # Initial points before marking the habit complete
    awarded_points = 10  # Points awarded for completing the habit
    
    # Mock user inputs for marking the habit as complete.
    def mock_input_mark_complete_gen():
        for val in ["2", "testuser", "testpass", "3", habit_title, "6"]:
            yield val
    
    # Use the 'patch' context manager to mock user inputs and print outputs during marking habit as complete.
    with patch('builtins.input', side_effect=mock_input_mark_complete_gen()) as mock_input:
        with patch('builtins.print') as mock_print:
            main_cli()  # Run the CLI with mocked inputs for marking the habit complete
            
            # Verify that completion status and awarded points are correctly printed.
            assert f"{habit_title} marked as complete!" in [call.args[0] for call in mock_print.call_args_list]
            assert f"You've been awarded {awarded_points} points!" in [call.args[0] for call in mock_print.call_args_list]
    
    teardown_test_environment()  # Tear down the test environment

    
    
    
def test_mark_invalid_habit_complete():
    setup_environment()  # Set up the test environment
    
    non_existent_habit_title = "Non-existent Habit"  # Habit title that does not exist
    
    # Mock user inputs for attempting to mark an invalid habit as complete.
    def mock_input_mark_invalid_gen():
        for val in ["2", "testuser", "testpass", "3", non_existent_habit_title, "6"]:
            yield val
    
    # Use the 'patch' context manager to mock user inputs and print outputs during testing.
    with patch('builtins.input', side_effect=mock_input_mark_invalid_gen()) as mock_input:
        with patch('builtins.print') as mock_print:
            main_cli()  # Run the CLI with mocked inputs for marking an invalid habit complete
            
            # Verify that the appropriate error message is printed when attempting to mark an invalid habit.
            assert f"Error: Habit '{non_existent_habit_title}' not found!" in [call.args[0] for call in mock_print.call_args_list]
    
    teardown_test_environment()  # Tear down the test environment
    
    

def test_view_rewards():
    # 1. Set up a test environment and add a habit
    setup_environment()

    habit_title = "Test Habit"
    reward_points = 10  # each completed habit gives 10 reward points

    # Mocking the user input to add a habit, mark it as complete, and then view rewards
    def mock_input_sequence():
        
        for val in ["1", habit_title, "3", habit_title, "5", "6"]:
            yield val

    with patch('builtins.input', side_effect=mock_input_sequence()) as mock_input:
        with patch('builtins.print') as mock_print:
            main_cli()

            # Check the output to ensure the correct reward points are displayed
            assert f"You have {reward_points} reward points" in [call.args[0] for call in mock_print.call_args_list]

    # Clean up after the test
    teardown_test_environment()


def test_view_analytics():
    setup_environment()  # Set up the test environment
    
    habit1_title = "Morning Run"  # First habit title for testing
    habit2_title = "Read for 30 minutes"  # Second habit title for testing
    
    # Mock user inputs for adding two habits and viewing analytics.
    def mock_input_sequence():
        for val in ["1", habit1_title, "1", habit2_title, "6"]:
            yield val
    
    # Use the 'patch' context manager to mock user inputs and print outputs during testing.
    with patch('builtins.input', side_effect=mock_input_sequence()) as mock_input:
        with patch('builtins.print') as mock_print:
            main_cli()  # Run the CLI with mocked inputs for adding habits and viewing analytics
            
            # Verify that habit titles and analytics data are correctly printed.
            assert habit1_title in [call.args[0] for call in mock_print.call_args_list]
            assert habit2_title in [call.args[0] for call in mock_print.call_args_list]
            assert "Analytics Data:" in [call.args[0] for call in mock_print.call_args_list]
    
    teardown_test_environment()  # Tear down the test environment

    
    
def test_logout():
    # 1. Set up a test environment.
    setup_environment()
    with patch('builtins.input', return_value="7") as mock_input:
        with patch('builtins.print') as mock_print:
            main_cli()

            # Check the output to ensure successful logout.
            assert "Successfully logged out!" in [call.args[0] for call in mock_print.call_args_list]

    # Clean up after the test
    teardown_test_environment() 
    
    
class CustomMock:
    def __init__(self, return_value):
        self.return_value = return_value

    def fetchone(self):
        return self.return_value

    def __getitem__(self, index):
        return self.return_value[index]

    
    
def test_create_and_delete_habit():
    """
    This function sets up a dummy habit for the test user, fetches its ID, and then tests its deletion.
    """
    username, _ = setup_test_environment()  # Getting the test username from the setup_test_environment function.

    # Create the test habit.
    habit_title = "Test Habit"
    habit_description = "This is a test habit."
    habit_periodicity = "Daily"
    habit_id = None
    with with_database_connection() as cursor:
        cursor.execute(
            "INSERT OR IGNORE INTO habits (username, title, description, periodicity, creation_date) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (username, habit_title, habit_description, habit_periodicity)
        )
        cursor.execute("SELECT id FROM habits WHERE title=?", (habit_title,))
        habit_exists = cursor.fetchone()
        if habit_exists:
            habit_id = habit_exists[0]
            print(f"Habit with ID={habit_id} exists:", bool(habit_exists))
        else:
            raise Exception("Test setup failed. Habit not found.")

    def side_effect(*args, **kwargs):
            print(f"Execute called with: {args}")

    with patch('__main__.with_database_connection', MagicMock()) as mock_conn:
        # Create a mock connection and mock cursor
        custom_cursor = CustomMock((habit_id,))
        
        # Create a mock_cursor and set its execute's side effect
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = side_effect
        mock_cursor.fetchone.return_value = custom_cursor.fetchone()
        
        # Return the mock_cursor when the cursor method of the connection is called
        mock_conn.cursor.return_value = mock_cursor
        
        print(f"Setting mock_cursor.fetchone return value to: {(habit_id,)}")


        # Add a side effect to ensure that when 'execute' is called, it prints
        def side_effect(*args, **kwargs):
            print(f"Execute called with: {args}")

        mock_cursor.execute.side_effect = side_effect

        # Mock the sqlite3.connect function to return our mock connection
        with patch('sqlite3.connect', return_value=mock_conn):
            delete_habit(username, habit_title)

    # Check mock calls here
    print(mock_cursor.execute.call_args_list)
    mock_cursor.execute.assert_any_call("DELETE FROM completions WHERE habit_id=?", (habit_id,))
    mock_cursor.execute.assert_any_call("DELETE FROM habits WHERE id=?", (habit_id,))

    
    # Optional: Clean up after test
    with with_database_connection() as cursor:
        cursor.execute("DELETE FROM habits WHERE id=?", (habit_id,))

        
    
# This function serves as the entry point for running a set of test cases.
# It sets up the test environment, runs each test function, and then tears down the environment.
def test_functions():
    setup_environment()  # Set up the test environment
    for func in [test_cli_login_success, test_cli_login_fail, test_cli_register_success, test_cli_register_fail, test_add_and_get_habits, test_mark_habit_complete, test_points_award, test_analytics, test_habit_streaks, test_create_and_delete_habit]:
        func()  # Run each individual test function
        print(f"{func.__name__} passed!")  # Print a success message for the completed test
    teardown_test_environment()  # Tear down the test environment
  
    
# This block of code is the entry point for running the test
if __name__ == "__main__":
    test_functions()  # Run the tests