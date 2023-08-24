1. Habit Tracker CLI

This is a Command Line Interface (CLI) application designed to help users track their habits and monitor their progress. Users can register, log in, add habits, mark habits as complete, view analytics, and more, all through a text-based interface.

Getting Started

1.1. Clone the Repository:
   Clone this repository to your local machine using Git.

1.2. Dependencies:
   Make sure you have Python 3.x installed on your system.

1.3. Install Required Libraries:
   Run the following command to install the required libraries: pip install sqlite3

1.4. Run the CLI:
Navigate to the project directory in your terminal and run the following command: python cli.py


This will start the Habit Tracker CLI and guide you through the available options.

2. Usage

- When you run the CLI, you'll be presented with options to register, log in, or quit.
- After logging in, you can add habits, view your habits, mark habits as complete, check your rewards, view analytics, or log out.

Important Notes

- Habits are stored in an SQLite database.
- The application supports the tracking of points and rewards for habit completion.
- Reminders can be set for habits with a specified periodicity.
- Analytics provide insights into your habit tracking progress.
- The CLI interface is text-based, so follow the prompts to navigate through the options.

3. Logging in as TeeLv

To log in as user TeeLv, ensure that the provided SQLite database file is located in the same directory as the script or adjust the path in the code accordingly. The predefined credentials for TeeLv are:

Username: TeeLv
Password: 12

Run the provided script and follow the login prompt. If the login is successful, the script will automatically populate TeeLv's habits, reminders, and completions.

Habit Descriptions for TeeLv
TeeLv has been predefined with 5 habits as follows:

- 'Morning Run'
Description: Run for 30 minutes every morning
Periodicity: Daily
Reminder: None

- 'Read Book'
Description: Read a book for 1 hour
Periodicity: Daily
Reminder: Daily at 13:00

- 'Weekly Meditation'
Description: Meditate for 2 hours every weekend
Periodicity: Weekly
Reminder: Weekly at 10:30

- 'Guitar Practice'
Description: Practice playing the guitar for 1 hour
Periodicity: Daily
Reminder: None

- 'Learn 50 Words in Thai'
Description: Learn 50 words from a foreign language
Periodicity: Monthly
Reminder: None

4. Reward System

- Points and Broken Streaks

Upon successful login, the system will check for any broken streaks for TeeLv's habits. Every time a streak is broken, TeeLv will be penalized by deducting 10 points. However, this deduction is executed only once on a given date. This means if TeeLv logs out and logs back in on the same date, the points will not be deducted again.

For example, if TeeLv has broken 3 streaks today and hasn't logged in until today, 30 points will be deducted upon the first login. Subsequent logins on the same day will not lead to further deductions.

To check the total points for TeeLv, you can use option "4" in the menu. This will provide you with the current point balance for TeeLv.

- Explanation for Points Deduction

The rationale for the points system is to motivate the user to maintain consistency in their habits. By penalizing broken streaks, we hope to encourage users like TeeLv to stick to their habits and achieve their goals. The system is designed to be fair by ensuring that points are deducted only once for a specific date of a log in, even if the user logs in multiple times on the date.

5. To run the Tests: Navigate to the project directory in your terminal and run the following command: python test.py
   
6. Technology Stack
- Language: Python
- DataBase: SQLite
