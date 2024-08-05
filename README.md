# Habit Tracker Plus (HTP)


HTP is a robust and easy-to-use software that monitors your progress in developing habits. It generates assessment 
metrics from your day-to-day activities to provide you with detailed progress reports on your level of compliance. 

Good habits are hard to develop but bad ones are even harder to drop. HTP is the quiet companion in your corner urging 
you on, as you embark on your journey of self-improvement. 


## What it is

With HTP, you can preset your target habits along with their respective time-based conditions. Each time you complete a 
habit and notify HTP, your progress report is updated. When you consecutively complete a habit, you are said to be on a 
streak. But when there is a slip, the streak is broken and a new one is started. At your convenience, you may view the 
progress reports for all your habits or for any particular habit.

## Features
* **Add Habit** allows you to add a habit task and choose the routine cycle; for example, daily or weekly 
* **View Habits** allows you see all your preset habits but if you need to see a particular habit or group of habits, 
go to **Analyze**
* **Add Events** helps to inform HTP you carried out a habit task
* **View Events** displays all the records of times you carried out a particular habit task.
* **Analyze** let you interact more granularly with HTP. You can view the current and longest streak record for a habit,
a habit settings and associated events et cetera. You can also carry out comparative analysis on your habit records, 
for example, you can view all habits with the same periodicity, all habit streaks (this includes each habit's current 
streak and the highest streak ever achieved for the habit) and your longest streak record ever for an active habit!
* **Edit** helps you correct any errors made while inputting your habit or habit event details. Please note that if you 
make a mistake in a habit name, you can not edit it. You may however, delete it and recreate the habit. You may also 
terminate a habit by selecting **Stop Habit** once you are satisfied with your progress. But note that any habit stopped 
would no longer be monitored by HTP. 
* **Delete** allows you to remove any habit or habit event(s) from your records. But note that when you delete a habit, 
all events associated with the habit will also be deleted.
* **Exit** closes the HTP application 

## Installation

'''
pip install -r requirements.txt

'''

## Usage
Start

'''
python main.py
'''

and follow instructions on screen


## Tests

'''
pytest .
'''

## Limitations
HTP currently support only Daily and Weekly habits. Support for Monthly and Yearly habits will be included in my next 
version.

## Acknowledgement
* Special thanks to the Python Team at International University for Applied Sciencies (IUBH), Berlin Germany, for 
their guidance and support throughout the development of this software especially Prof Max Pumperla for his patient 
assistance and tips.

