from db import (save_habit, save_event, get_habit, get_events, get_event, get_events_by_name_event_date, delete_event,
                delete_events, delete_habit, update_habit, update_event)
from analyse import calculate_counter


class Counter:
    """Counter class."""

    def __init__(self, name: str, description="", start_date="",
                 periodicity="Daily", cut_off_style="IGNORE",
                 cut_off_time="00:00:00", habit_status="ACTIVE"):
        """Initialize the counter class.

        :params: name: is the name of the habit
        :params: description: is the description of the habit
        :params: start_date: is the datetime the app starts analyzing events for
            the habit. When omitted, current datetime is assumed
        :params: periodicity: is the expected frequency for the habit - Daily
                            or Weekly. When omitted, Daily is assumed
        :params: cut_off_style: this shows if the time the habit is undertaken
            is significant. Values include IGNORE/ON/BEFORE/AFTER. When omitted
            IGNORE is assumed; meaning the time event occurred is NOT important
        :params: cut_off_time: is the threshold time for the habit. When
            omitted 00:00:00 is assumed.
        :params: habit_status: is the status of the habit. Values include
                ACTIVE/COMPLETED. Only ACTIVE habits are analyzed.
        """
        self.name = name.upper()
        self.description = description
        self.periodicity = periodicity
        self.start_date = start_date
        self.cut_off_style = cut_off_style
        self.cut_off_time = cut_off_time
        self.habit_status = habit_status

        self.streak = 0
        self.highest_streak = 0

    def calculate_streak(self):
        """Assign the calculated streak count and the highest streak."""
        res = calculate_counter(self.name)
        if isinstance(res, str):
            return res
        else:
            self.streak = res.streak
            self.highest_streak = res.max_streak

    def reset(self):
        """Reset counter and set counter streak and highest_streak to 0."""
        res = self._get_habit(self.name)
        if not isinstance(res, str):
            self.name = res.name.upper()
            self.description = res.description
            self.periodicity = res.periodicity
            self.start_date = res.start_date
            self.cut_off_style = res.cut_off_style
            self.cut_off_time = res.cut_off_time
            self.habit_status = res.habit_status

        self.streak = 0
        self.highest_streak = 0

    def __str__(self):
        """Display habit name, streak and highest streak for the habit."""
        return f'{self.name} : Streak = {self.streak}, Highest Streak = {self.highest_streak}'

    def add_habit(self):
        """Save a new habit to the sqlite3 database."""
        res = save_habit(self.name, self.description, self.start_date,
                         self.periodicity, self.cut_off_style,
                         self.cut_off_time, self.habit_status)
        return res

    def update_my_habit(self, description='', start_date='', periodicity='', cut_off_style='', cut_off_time=''):
        """Update a habit in the sqlite3 database."""

        res = update_habit(self.name, description, start_date, periodicity, cut_off_style, cut_off_time)
        if 'SUCCESS' in res:
            self.reset()
            return f'SUCCESS: Habit {self.name} changes have been saved!'
        else:
            return res

    def _get_habit(self, name: str):
        """Get a habit from the sqlite3 database."""
        return get_habit(name)

    def stop_my_habit(self):
        """Deactivate the current habit."""
        res = update_habit(self.name, '', '', '',
                           '', '','COMPLETED')
        if 'SUCCESS' in res:
            self.habit_status = 'COMPLETED'

    def delete_my_habit_plus_events(self):
        """Delete the current habit plus all associated habit events."""

        get_events_if_exist = self.get_events()
        if isinstance(get_events_if_exist, list):
            res = self.delete_habit_events()
            if 'ERROR' in res:
                return res
            else:
                return delete_habit(self.name)
        else:
            return delete_habit(self.name)

    def add_event(self, event_date: str = ''):
        """
        Save a new event carried out for the habit to the sqlite3 database.

        :params: event_date: the date and time the event was performed. Current
                system date is assumed if this parameter is omitted
        """
        res = save_event(self.name, event_date)
        return res

    def get_events(self):
        """Retrieve all events for the current habit."""
        return get_events(self.name)

    def get_event_by_event_id(self, event_id: str):
        """Retrieve all events for the current habit matching the given date

        :Params: event_id:id of habit event as a string
        :return: Returns a list of event(s) matching the event_id
        """
        return get_event(event_id)

    def get_event(self, event_date: str):
        """Retrieve all events for the current habit matching the given date

        :Params: event_date:date event occurred as a string
        :return: Returns a list of event(s) matching the habit name and event date
        """
        return get_events_by_name_event_date(self.name, event_date)

    def update_my_event(self, event_id: str, habit_name='', event_date=''):
        """Update an event for the current habit.

        :params: event_id: unique uuid string identifying the event to be updated
        :params: habit_name: name of the event habit
        :params: event_date: date when event occurred
        """
        return update_event(event_id, habit_name, event_date)

    def delete_my_event(self, event_id: str):
        """Delete an event for the current habit.

        :params: event_id: unique uuid string identifying the event to be deleted
        :return: status of the deleted event or error encountered
        """
        return delete_event(event_id)

    def delete_habit_events(self):
        """Delete all events for the current habit."""

        return delete_events(self.name)
