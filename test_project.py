import gc
from counter import Counter
from db import create_data_storage
from analyse import (calculate_all_counters, calculate_counter, get_all_habits, get_habits_periodically,
                     habit_with_longest_streak)


class TestCounter:
    def setup_method(self):
        create_data_storage('test.db')

        self.habit = Counter('Exercise', 'Keeping fit for the next olympic',
                             '2024-01-01 07:00:00', 'Daily', 'BEFORE',
                             '08:00:00', 'Active')
        self.habit.add_habit()

    def test_counter(self):

        self.habit = Counter('Christian Meetings', 'Fellowship with family',
                             '2024-01-05 05:00:00', 'Weekly', 'IGNORE',
                             '06:00:00', 'Active')
        self.habit.add_habit()
        assert self.habit.name == 'CHRISTIAN MEETINGS'
        assert self.habit.description == 'Fellowship with family'
        assert self.habit.start_date == '2024-01-05 05:00:00'
        assert self.habit.periodicity == 'Weekly'
        assert self.habit.cut_off_style == 'IGNORE'
        assert self.habit.cut_off_time == '06:00:00'
        assert self.habit.habit_status == 'Active'

        self.habit.add_event('2024-01-02 06:00:00')
        self.habit.add_event('2024-01-07 06:02:01')

        self.habit.add_event('2024-01-14 08:00:00')
        self.habit.add_event('2024-01-21 06:00:00')
        self.habit.add_event('2024-01-28 06:02:01')

        self.habit.add_event('2024-02-04 08:00:00')

        christian_meeting_events = self.habit.get_events()
        assert len(christian_meeting_events) == 6

        get_daily_habits = get_habits_periodically('Daily')
        assert len(get_daily_habits) == 1

        get_weekly_habits = get_habits_periodically('Weekly')
        assert len(get_weekly_habits) == 1

        all_monitored_habits = get_all_habits()
        assert len(all_monitored_habits) == 2

        all_streak = calculate_counter('Christian Meetings')
        assert all_streak.streak == 4
        assert all_streak.max_streak == 4

        longest_streak = habit_with_longest_streak()
        assert longest_streak.max_streak == 4

        self.habit2 = Counter('exercise')
        self.habit2.add_event('2024-01-01 07:00:01')

        self.habit3 = Counter('Study', 'Reading is fun', '2024-01-01 07:00:01', 'Daily',
                              'IGNORE', '00:00:00', 'ACTIVE')
        self.habit3.add_habit()
        self.habit3.add_event('2024-01-01 07:00:01')
        self.habit3.add_event('2024-01-02 07:00:01')

        all_habit_counters = calculate_all_counters()
        assert all_habit_counters[0].max_streak == 1
        assert len(all_habit_counters) == 3

        self.habit2.update_my_habit(start_date='2024-01-05 06:00:00')
        assert self.habit2.start_date == '2024-01-05 06:00:00'

        self.habit2.stop_my_habit()
        assert self.habit2.habit_status == 'COMPLETED'

        self.habit3.delete_my_habit_plus_events()

        # testing delete of habits without events
        self.habit4 = Counter('Game', 'Reading is not fun', '2024-01-01 07:00:01', 'Daily',
                              'IGNORE', '00:00:00', 'ACTIVE')
        self.habit4.add_habit()
        self.habit4.delete_my_habit_plus_events()

        # Stopped and Deleted Habits are not monitored
        all_monitored_habits = get_all_habits()
        assert len(all_monitored_habits) == 1

        original_event = self.habit.get_event('2024-01-28 06:02:01')
        if len(original_event) > 0:
            self.habit.update_my_event(original_event[0].event_id, self.habit.name, '2024-01-29 06:02:01')
            editted_event = self.habit.get_event_by_event_id(original_event[0].event_id)
            assert editted_event.event_id == original_event[0].event_id
            assert editted_event.event_date == '2024-01-29 06:02:01'

            self.habit.delete_my_event(original_event[0].event_id)
            # one event less than the previous number above
            christian_meeting_events = self.habit.get_events()
            assert len(christian_meeting_events) == 5

    def test_single_counter(self):
        self.habit = Counter('exercise')
        self.habit.add_event('2024-01-01 07:00:01')
        self.habit.calculate_streak()

        assert self.habit.streak == 1
        assert self.habit.highest_streak == 1

    def test_multiple_counter(self):
        self.habit = Counter('exercise')
        self.habit.add_event('2023-12-31 07:00:01')
        self.habit.add_event('2024-01-01 07:00:01')
        self.habit.add_event('2024-01-02 06:02:01')

        self.habit.add_event('2024-01-03 08:00:00')
        self.habit.calculate_streak()

        # Habit events before the habit start date are excluded from the analysis
        assert self.habit.streak == 0
        assert self.habit.highest_streak == 2

    def test_random_counter(self):
        self.habit = Counter('exercise')
        self.habit.add_event('2024-01-02 06:02:01')
        self.habit.add_event('2023-12-31 07:00:01')
        self.habit.add_event('2024-01-03 08:00:00')
        self.habit.add_event('2024-01-01 07:00:01')

        self.habit.calculate_streak()

        assert self.habit.streak == 0
        assert self.habit.highest_streak == 2

    def teardown_method(self):
        import sqlite3
        from contextlib import closing
        import os

        dbname = 'test.db'

        with closing(sqlite3.connect(dbname)) as connection:
            with connection:
                cursor = connection.cursor()
                cursor.execute("delete from events")
                connection.commit()
                cursor.close()
                del cursor
                del connection
                gc.collect(2)

        os.remove(dbname)
