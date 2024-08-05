from db import get_habit, get_habits, get_events, get_habits_by_periodicity
from datetime import datetime, timedelta
from collections import namedtuple
from operator import attrgetter


def _get_habit_streak(habit_name: str):
    """Gets the current streak and highest streak for the current habit.

    :params: habit_name: target habit name whose streak details is requested
    :return: returns a namedtuple containing the current streak and highest streak
        the requested habit
           """
    habit_response = get_habit(habit_name)
    if 'ERROR' in habit_response:
        return habit_response
    elif not (habit_response.habit_status == 'ACTIVE'):
        return f'ERROR: Habit {habit_name} is {habit_response.habit_status}. Only \
            ACTIVE habits are analysed'
    else:
        habit_events_response = get_events(habit_name)
        if 'ERROR' in habit_events_response:
            return habit_events_response
        else:
            next_date_days_increment = 1
            if habit_response.periodicity == 'Weekly':
                next_date_days_increment = 7
            habit_startdate = datetime.fromisoformat(habit_response.start_date)
            '''If the habit cut_off_style is not IGNORE, that means a specific
            time is required for this habit'''
            if not (habit_response.cut_off_style == 'IGNORE'):
                cut_off_time_parts = habit_response.cut_off_time.split(':')
                if len(cut_off_time_parts) == 3:
                    habit_startdate = datetime(habit_startdate.year,
                                               habit_startdate.month,
                                               habit_startdate.day,
                                               int(cut_off_time_parts[0]),
                                               int(cut_off_time_parts[1]),
                                               int(cut_off_time_parts[2]))
            # exclude events that occurred before the habit start date
            valid_events = [x for x in habit_events_response if
                            habit_startdate.date() <=
                            datetime.fromisoformat(x.event_date).date()]
            streak = 0
            max_streak = 0
            if valid_events:
                # sorted the list for sequential analysis
                valid_events = sorted(valid_events, key=attrgetter('event_date'))
                for x in valid_events:
                    event_credible_flag = 0
                    event_datetime = datetime.fromisoformat(x.event_date)
                    if habit_startdate.date() == event_datetime.date():
                        if habit_response.cut_off_style == 'IGNORE':
                            event_credible_flag = 1
                        elif habit_response.cut_off_style == 'ON':
                            if event_datetime.time() == habit_startdate.time():
                                event_credible_flag = 1
                        elif habit_response.cut_off_style == 'AFTER':
                            if event_datetime.time() > habit_startdate.time():
                                event_credible_flag = 1
                        elif habit_response.cut_off_style == 'BEFORE':
                            if event_datetime.time() < habit_startdate.time():
                                event_credible_flag = 1
                        else:
                            return f'Unknown cut_off_style  {habit_response.cut_off_style}.'

                        if event_credible_flag:
                            streak += 1
                            max_streak = max(max_streak, streak)
                        else:
                            # start new streak
                            streak = 0

                        habit_startdate += timedelta(days=next_date_days_increment)
                    else:
                        # streak breaks reset streak,max_streak,habit_startdate
                        streak = 0
                        event_datetime += timedelta(days=next_date_days_increment)
                        habit_startdate = datetime(event_datetime.year,
                                                   event_datetime.month,
                                                   event_datetime.day,
                                                   habit_startdate.hour,
                                                   habit_startdate.minute,
                                                   habit_startdate.second)

                streak_data = namedtuple("Habit", "name streak max_streak")
                return streak_data(habit_name, streak, max_streak)
            else:
                return f'There are no events to analyze for habit {habit_name}'


def get_all_habits():
    """Retrieve all the habits existing in the sqlite3 database.

    :return: Returns a namedtuple list of all the habits existing in the
        database or a message showing no habit was found if empty
    """
    return get_habits()


def get_habits_periodically(frequency: str):
    """Retrieve all habits existing in the database by their periodicity.

    :params: frequency: this is the expected rate of carrying out habit -
        Daily or Weekly
    :return: Returns a namedtuple list of all the habits marching period
        existing in the database or a message showing no habit was found
    """
    return get_habits_by_periodicity(frequency)


def calculate_counter(habit_name: str):
    """
    Calculate the number of times a habit was consecutively undertaken.

    :params: habit_name: is the named habit that we want to estimate compliance
    :return: namedtuple of three items-habit name, current number of times
    habit was consecutively undertaken (streak) and the maximum streak ever
    attained for the habit
    """
    return _get_habit_streak(habit_name)


def calculate_all_counters():
    """
    Calculate the number of times all habits were consecutively undertaken.

    :return: namedtuple list of three items-habit name, current number of
    times habit was consecutively undertaken (streak) and the maximum streak
    ever attained for the habit
    """
    all_habits = get_habits()
    if all_habits:
        my_counters = []
        for x in all_habits:
            res = _get_habit_streak(x.name)
            # Just skip the habit details
            if not isinstance(res, str):
                my_counters.append(res)

        return my_counters
    else:
        return "There is no habit to analyze at the moment"


def habit_with_longest_streak():
    """
    Get the habit with the longest streak.

    :return: namedtuple of the habit with the longest streak
    """
    all_counters = calculate_all_counters()
    max_value = 0
    index = -1
    if all_counters:
        for x in all_counters:
            if x.max_streak > max_value:
                max_value = x.max_streak
                index = all_counters.index(x)
        return all_counters[index]
    else:
        return "There is no habit to analyze at the moment"
