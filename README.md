**Habit Tracker CLI** 📋
   This is a Command Line Interface (CLI) application designed to help users track their habits and monitor their progress. Users can register, log in, add habits, mark habits as complete, view analytics, and more, all through a text-based interface.

🚀 **Getting Started**

   1️⃣ Clone the Repository: *git clone https://github.com/VixitIU/HabitTrackingApp*
   
   2️⃣ Dependencies
   Make sure you have Python 3.x installed on your system.
   
   3️⃣ Install Required Libraries
   Run the following command to install the required libraries: *pip install sqlite3*
   
   4️⃣ Run the CLI
   Navigate to the project directory in your terminal and run the following command: *python cli.py*
   This will start the Habit Tracker CLI and guide you through the available options.

📘 **Usage**
   When you run the CLI, you'll be presented with options to register, log in, or quit.
   After logging in, you can add habits, view your habits, mark habits as complete, check your rewards, view analytics, or log out.

🔑 **Logging in as TeeLv**
   To log in as user TeeLv, ensure that the provided SQLite database file is located in the same directory as the script or adjust the path in the code accordingly.
   Username: TeeLv
   Password: 12
   Run the provided script and follow the login prompt. If the login is successful, the script will automatically populate TeeLv's habits, reminders, and completions.

📜 **Pre-defined Habit Descriptions for TeeLv User**
   TeeLv has been predefined with 5 habits as follows:

   *Morning Run:*
   Description: Run for 30 minutes every morning
   Periodicity: Daily
   Reminder: None
   
   *Read Book:*
   Description: Read a book for 1 hour
   Periodicity: Daily
   Reminder: Daily at 13:00
   
   *Weekly Meditation:*
   Description: Meditate for 2 hours every weekend
   Periodicity: Weekly
   Reminder: Weekly at 10:30
   
   *Guitar Practice:*
   Description: Practice playing the guitar for 1 hour
   Periodicity: Daily
   Reminder: None
   
   *Learn 50 Words in Thai:*
   Description: Learn 50 words from a foreign language
   Periodicity: Monthly
   Reminder: None

🏆 **Reward System**

   *Points and Broken Streaks:*
   Upon successful login, the system will check for any broken streaks for TeeLv's habits. Every time a streak is broken, TeeLv will be penalized by deducting 10 points. However, this deduction is executed only once on a given date. This means if TeeLv logs out and logs back in on the same date, the points will not be deducted again. *Example:* If TeeLv has broken 3 streaks today and hasn't logged in until today, 30 points will be deducted upon the first login. Subsequent logins on the same day will not lead to further deductions.
   
   *Check Points:*
   To check the total points for TeeLv, use option "4" in the menu.
   
   *Explanation for Points Deduction:*
   The rationale for the points system is to motivate the user to maintain consistency in their habits. By penalizing broken streaks, we hope to encourage users like TeeLv to stick to their habits and achieve their goals.

📊 **To Run the Tests**
   Navigate to the project directory in your terminal and run the following command: *python tests.py*

🛠 **Technology Stack**

   Language: Python
   Database: SQLite
