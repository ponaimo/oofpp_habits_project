import sqlite3
from datetime import datetime, timedelta
from collections import namedtuple
import uuid
db_name = ''


def create_data_storage(name="main.db"):
    """Create the sqlite3 database and tables if not existing yet.

    :params: name: database name to be used for the application
    :return: message showing if database and tables were successfully created
    """
    global db_name
    db_name = name
    return _create_tables()


def _execute_query(sql_query: str, parameters=()):
    """Execute all other queries.

    :params: sql_query: sql query string to be executed
    :params: parameters: set of parameters needed by the sql query. if just one
        parameter, add a trailing comma eg(one_parameter,)
    :result: cursor for the connection is returned
    """
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query, parameters)
            conn.commit()
        return cursor
    except Exception as ex:
        return ex.args


def _format_query_single_result(cursor):
    """Return single item from query.

    :params: cursor: cursor from the sql connection.
    :return: returns single item found or error message if not found
    """
    result = cursor.fetchone()
    if result:
        return result
    else:
        return "ERROR: Requested item NOT found!"


def _format_query_results(cursor):
    """Return multiple items from query.

    :params: cursor: cursor from the sql connection.
    :return: returns list of multiple items found or error message if not found
    """
    result = cursor.fetchall()
    # print('Count of items: ' + len(result).__str__())
    if result:
        formatted_results = []
        for row in result:
            # formatted_results.append(", ".join([str(i) for i in row]))
            formatted_results.append(row)
        return formatted_results
    else:
        return 'ERROR: Requested item(s) NOT found!'


def _create_tables():
    """Create the tables - habits and events, used by the counter app.

    :return: returns status report of the table creation
    """
    query_habit = """CREATE TABLE IF NOT EXISTS habits (
            name TEXT NOT NULL PRIMARY KEY,
            description TEXT,
            entry_date TEXT,
            start_date TEXT,
            periodicity TEXT,
            cut_off_style TEXT,
            cut_off_time TEXT,
            habit_status TEXT
            )
            """
    result_habit = _execute_query(query_habit)
    query_events = """CREATE TABLE IF NOT EXISTS events (
            event_id   TEXT NOT NULL PRIMARY KEY,
            habit_name TEXT,
            event_date TEXT,
            FOREIGN KEY (habit_name) REFERENCES habits (name)
            )
            """
    result_events = _execute_query(query_events)
    return f"Habit Table Status: {result_habit}, Counter Table Status: {result_events}"


def _convert_time_to_24hrs_format(value: str):
    """Convert 12hrs datetime value to 24hrs format.

    :params: value: datetime value. Input format is YYYY-MM-DD hh:mm:ss AM
    :return: returns datetime string value in equivalent 24hrs format
    """
    value = value.lower()
    pm_add_twelve_hours = 0

    if 'pm' in value:
        pm_add_twelve_hours = 12
        value = value.replace("pm", "")
    elif 'am' in value:
        value = value.replace("am", "")

    value = value.rstrip()
    value = value.lstrip()

    return value, pm_add_twelve_hours


def _is_valid_datetime(value: str):
    """Validate the date time input. Format YYYY-MM-DD hh:mm:ss AM.

    :params: value: datetime value. Input format is YYYY-MM-DD hh:mm:ss AM
    :return: returns valid datetime string - YYYY-MM-DD hh:mm:ss or the error
    """
    value, patch_to_24hrs = _convert_time_to_24hrs_format(value)

    try:
        check_date = datetime.fromisoformat(value)
        valid_datetime = datetime(check_date.year, check_date.month,
                                  check_date.day,
                                  check_date.hour + patch_to_24hrs,
                                  check_date.minute, check_date.second)
        return valid_datetime.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as ex:
        return f"ERROR: {ex.args}. Sample Date is 2024-01-31 05:19:03 AM"


def _is_valid_time(value: str):
    """Validate the time input. Accepted input format hh:mm:ss AM.

    :params: value: time value. Input format is hh:mm:ss A
    :return: returns valid time string - hh:mm:ss or the error message
    """
    value, patch_to_24hrs = _convert_time_to_24hrs_format(value)

    try:
        check_time = datetime.fromisoformat("1111-01-01 " + value)
        valid_time = datetime(check_time.year, check_time.month,
                              check_time.day,
                              check_time.hour + patch_to_24hrs,
                              check_time.minute, check_time.second)
        return valid_time.strftime("%H:%M:%S")
    except Exception as ex:
        return f"ERROR: {ex.args}. Sample Time is 05:19:03 AM"


def _validate_habit(name: str, description="", start_date="", periodicity="",
                    cut_off_style="", cut_off_time="", habit_status=""):
    """Validate the fields for a habit.

    :params: name: is the name of the habit
    :params: description: is the description of the habit
    :params: start_date: is the datetime the app starts analyzing events for
                        the habit.
    :params: periodicity: is the expected frequency for the habit - Daily
                        or Weekly.
    :params: cut_off_style: this shows if the time the habit is undertaken
        is significant. Values include IGNORE/ON/BEFORE/AFTER.
    :params: cut_off_time: is the threshold time for the habit.
    :params: habit_status: is the status of the habit. Values include
            ACTIVE/COMPLETED.
    :return: returns a habit with a list of all its valid properties -
        [name, description, start_date, periodicity, cut_off_style,
        cut_off_time, habit_status] or an error stating any invalid property
        value encountered
    """
    if not name:
        return 'ERROR: habit name is required'
    else:
        name = name.upper()

    if start_date:
        result = _is_valid_datetime(start_date)
        if 'ERROR' in result:
            return result
        else:
            start_date = result

    if periodicity:
        periodicity = periodicity.capitalize()
        if not (periodicity == 'Daily' or periodicity == 'Weekly'):
            return f'ERROR: Allowed periodicity are Daily or Weekly NOT [{periodicity}]'

    if cut_off_style:
        cut_off_style = cut_off_style.upper()
        if not (cut_off_style == 'IGNORE' or cut_off_style == 'ON' or
                cut_off_style == 'BEFORE' or cut_off_style == 'AFTER'):
            return f'ERROR: Allowed cut_off_style are IGNORE/ON/BEFORE/AFTER not [{cut_off_style}]'

    if cut_off_time:
        result = _is_valid_time(cut_off_time)
        if 'ERROR' in result:
            return result
        else:
            cut_off_time = result

    if habit_status:
        habit_status = habit_status.upper()
        if not (habit_status == 'ACTIVE' or habit_status == 'COMPLETED'):
            return f'ERROR:Allowed habit_status are ACTIVE/COMPLETED not [{habit_status}]'

    return [name, description, start_date, periodicity, cut_off_style,
            cut_off_time, habit_status]


def save_habit(name: str, description: str, start_date="", periodicity="Daily",
               cut_off_style="IGNORE", cut_off_time="00:00:00",
               habit_status="ACTIVE"):
    """Save a new habit to the sqlite3 database.

    :params: name: is the name of the habit
    :params: description: is the description of the habit
    :params: start_date: is the datetime the app starts analyzing events for
        the habit. When omitted, current datetime is assumed
    :params: periodicity: is the expected frequency for the habit - Daily
                        or Weekly. When omitted, Daily is assumed
    :params: cut_off_style: this shows if the time the habit is undertaken
        is significant. Values include IGNORE/ON/BEFORE/AFTER. When omitted
        IGNORE is assumed; meaning the time event occurred is NOT important
    :params: cut_off_time: is the threshold time for the habit. When omitted
        00:00:00 is assumed.
    :params: habit_status: is the status of the habit. Values include
            ACTIVE/COMPLETED. Only ACTIVE habits are analyzed.
    :result: A message indicating the success or error encountered is returned
    """
    result = _validate_habit(name, description, start_date, periodicity,
                             cut_off_style, cut_off_time, habit_status)
    if isinstance(result, str):
        return result
    else:
        name, description, start_date, periodicity, cut_off_style, cut_off_time, habit_status = result

        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not start_date:
            start_date = current_date

        entry_date = current_date
        try:
            query = 'INSERT INTO habits VALUES(?, ?, ?, ?, ?, ?, ?, ?)'
            parameters = (name, description, entry_date, start_date,
                          periodicity, cut_off_style, cut_off_time,
                          habit_status)

            _execute_query(query, parameters)

            return 'Habit {} successfully created!'.format(name)
        except Exception as ex:
            return ex.args


def get_habits():
    """Retrieve all the habits existing in the sqlite3 database.

    :return: Returns a namedtuple list of all the habits existing in the
        database or a message showing no habit was found if empty
    """
    query = "SELECT * FROM habits where habit_status = 'ACTIVE' ORDER BY periodicity, name ASC"
    result = _format_query_results(_execute_query(query))
    if 'ERROR' in result:
        return result
    else:
        habit = namedtuple("Habit", ['name', 'description', 'entry_date',
                                             'start_date', 'periodicity',
                                             'cut_off_style',
                                             'cut_off_time',
                                             'habit_status'])

        return [habit(x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7])
                for x in result]


def get_habit(name: str):
    """Retrieve a specific habit with the name existing in the database.

    :params: name: name of the habit to be retrieve
    :return: Returns the namedtuple of the habit with the supplied name if it
    exists in the database or an error message if not found
    """
    query = "SELECT * FROM habits WHERE name=?"
    parameter = (name.upper(),)
    result = _format_query_single_result(_execute_query(query, parameter))
    if 'ERROR' in result:
        return result
    else:
        habit = namedtuple("Habit", ['name', 'description', 'entry_date',
                                             'start_date', 'periodicity',
                                             'cut_off_style',
                                             'cut_off_time',
                                             'habit_status'])
        current_habit = habit(result[0], result[1], result[2], result[3],
                              result[4], result[5], result[6], result[7])

        return current_habit


def get_habits_by_periodicity(frequency: str):
    """Retrieve all habits existing in the database by their periodicity.

    :params: frequency: this is the expected rate of carrying out habit -
        Daily or Weekly
    :return: Returns a namedtuple list of all the habits marching period
        existing in the database or a message showing no habit was found
    """
    query = "SELECT * FROM habits where periodicity=? and habit_status = 'ACTIVE' ORDER BY name ASC"
    parameter = (frequency.capitalize(),)
    result = _format_query_results(_execute_query(query, parameter))
    if 'ERROR' in result:
        return result
    else:
        habit = namedtuple("Habit", ['name', 'description', 'entry_date',
                                             'start_date', 'periodicity',
                                             'cut_off_style',
                                             'cut_off_time',
                                             'habit_status'])

        return [habit(x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7])
                for x in result]


def update_habit(name: str, description="", start_date="", periodicity="",
                 cut_off_style="", cut_off_time="", habit_status=""):
    """Edit records of an existing habit in the sqlite3 database.

    :params: name: is the name of the habit
    :params: description: is the description of the habit
    :params: start_date: is the datetime the app starts analyzing events for
        the habit.
    :params: periodicity: is the expected frequency for the habit - Daily
        or Weekly.
    :params: cut_off_style: this shows if the time the habit is undertaken
        is significant. Values include IGNORE/ON/BEFORE/AFTER.
    :params: cut_off_time: is the threshold time for the habit.
    :params: habit_status: is the status of the habit. Values include
            ACTIVE/COMPLETED. Only ACTIVE habits are analyzed.
    :result: A message indicating the success or error encountered is returned
    """
    if_exist = get_habit(name)
    if 'ERROR' in if_exist:
        return f'ERROR: Habit {name} does not exist!'
    else:
        result = _validate_habit(name, description, start_date, periodicity,
                                 cut_off_style, cut_off_time, habit_status)
        if isinstance(result, str):
            return result
        else:
            name, description, start_date, periodicity, cut_off_style,  cut_off_time, habit_status = result

        if description:
            query = "UPDATE habits set description=? WHERE name=?"
            parameters = (description, name)
            _execute_query(query, parameters)
        if start_date:
            query = "UPDATE habits set start_date=? WHERE name=?"
            parameters = (start_date, name)
            _execute_query(query, parameters)
        if periodicity:
            query = "UPDATE habits set periodicity=? WHERE name=?"
            parameters = (periodicity, name)
            _execute_query(query, parameters)
        if cut_off_style:
            query = "UPDATE habits set cut_off_style=? WHERE name=?"
            parameters = (cut_off_style, name)
            _execute_query(query, parameters)
        if cut_off_time:
            query = "UPDATE habits set cut_off_time=? WHERE name=?"
            parameters = (cut_off_time, name)
            _execute_query(query, parameters)
        if habit_status:
            query = "UPDATE habits set habit_status=? WHERE name=?"
            parameters = (habit_status, name)
            _execute_query(query, parameters)

        return f'SUCCESS: Habit {name} successfully updated!'


def delete_habit(name: str):
    """Delete a specific habit with the given name existing in the database.

    :params: name: name of the habit to be deleted
    :return: Returns a message that the named habit was successfully deleted
        from the sqlite3 database or that no habit was found matching the name
    """
    if_exist = get_habit(name)
    if 'ERROR' in if_exist:
        return f'ERROR: Habit {name} does not exist!'
    else:
        query = "DELETE FROM habits WHERE name=?"
        parameter = (name.upper(),)
        _execute_query(query, parameter)
        return f'Habit {name} has been deleted!'


def _event_exists(name: str, event_date: str):
    """Checks if event already exist using the habit name and event date.

        :params: name: name of the habit whose events are to be retrieved
        :Params: event_date:date event occurred as a string
        :return: Returns a list of event(s) matching the habit name and event date
        """
    get_existing_events = get_events(name)

    if not isinstance(get_existing_events, str):
        new_date = datetime.fromisoformat(event_date)
        same_day_events = []
        if isinstance(new_date, datetime):
            # creates the last second of the previous day
            date_before = datetime.fromisoformat((new_date - timedelta(days=1)).strftime("%Y-%m-%d") + ' 23:59:59')
            # creates the first second of the next day
            date_after = datetime.fromisoformat((new_date + timedelta(days=1)).strftime("%Y-%m-%d") + ' 00:00:00')

            same_day_events = [x for x in get_existing_events if (datetime.fromisoformat(x.event_date) >= date_before
                                                                  and datetime.fromisoformat(x.event_date) <= date_after)]
            # the above ensures that the date only checks for yyyy-mm-dd
        return same_day_events


def get_events_by_name_event_date(name: str, event_date: str):
    """Checks if event already exist using the habit name and event date.

        :params: name: name of the habit whose events are to be retrieved
        :Params: event_date:date event occurred as a string
        :return: Returns a list of event(s) matching the habit name and event date
        """
    return _event_exists(name, event_date)


def _check_event_exists_by_event_name_date(name: str, event_date: str):
    """Checks if event already exist using the habit name and event date.

    :params: name: name of the habit whose events are to be retrieved
    :Params: event_date:date event occurred as a string
    :return: Returns an error message if the event already exists, otherwise,
         a success message is returned advising you to continue with new event addition
    """
    same_day_events = _event_exists(name, event_date)
    if same_day_events:
        return 'ERROR: Event Already Exists!'
    else:
        return 'SUCCESS: Event was not found in the database'


def _validate_event(name: str, event_date=""):
    """Validate the fields for an event.

    :params: name: is the name of the habit whose event is being recorded
    :params: event_date: datetime when the habit was carried out
    :return: returns an event with a list of all its valid properties -
    [name,entry_date] or error stating any invalid property value encountered
    """
    if not name:
        return 'ERROR: habit name for event is required'
    else:
        result = get_habit(name)
        if 'ERROR' in result:
            return f'ERROR: Habit {name} does not exist'

    if event_date:
        result = _is_valid_datetime(event_date)
        if 'ERROR' in result:
            return result
        else:
            event_date = result
    return [name.upper(), event_date]


def save_event(name: str, event_date=""):
    """Save a new habit event to the sqlite3 database.

    :params: name: is the name of the habit
    :params: event_date: datetime when the habit was carried out
    :result: A message indicating the success or error encountered is returned
    """
    result = _validate_event(name, event_date)
    if isinstance(result, str):
        return result
    else:
        name, event_date = result
        if not event_date:
            event_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        check_event_exist = _check_event_exists_by_event_name_date(name, event_date)
        if 'SUCCESS' in check_event_exist:
            query = "INSERT INTO events VALUES(?, ?, ?)"
            event_id = str(uuid.uuid4())
            parameters = (event_id, name, event_date)

            _execute_query(query, parameters)
            return 'Event for habit {} was successfully uploaded!'.format(name)
        else:
            return check_event_exist


def get_event(event_id: str):
    """Retrieve a habit event with the event_id  existing in the database.

    :params: event_id: event_id of the habit event to be retrieved
    :return: Returns namedtuple of the habit event with the supplied event_id
        existing in the database or a message showing no habit event was found
        matching the event_id
    """
    query = "SELECT * FROM events WHERE event_id=?"
    parameter = (event_id,)
    result = _format_query_single_result(_execute_query(query, parameter))
    if 'ERROR' in result:
        return result
    else:
        habit_event = namedtuple("Event", ['event_id', 'habit_name', 'event_date'])
        current_event = habit_event(result[0], result[1], result[2])

        return current_event


def get_events(name: str):
    """Retrieve an ordered by event_date list of events for the habit name.

    :params: name: name of the habit whose events are to be retrieve
    :return: Returns a list of namedtuple events for the supplied habit name
        existing in the database or a message showing no habit event was found
        matching the habit name
    """
    query = 'SELECT * FROM events WHERE habit_name=?'
    parameter = (name.upper(),)
    result = _format_query_results(_execute_query(query, parameter))
    if 'ERROR' in result:
        return f'ERROR: There are no events for habit {name.upper()} in our database'
    else:
        habit_event = namedtuple("Event", ['event_id', 'habit_name', 'event_date'])

        return [habit_event(x[0], x[1], x[2]) for x in result]


def update_event(event_id: str, name, event_date):
    """Edit records of an existing habit event in the sqlite3 database.

    :params: event_id: event_id of the habit event to be updated
    :params: name: is the name of the habit
    :params: event_date: is the datetime when event occurred
    :result: A message indicating the success or error encountered is returned
    """
    if_exist = get_event(event_id)
    if 'ERROR' in if_exist:
        return f'ERROR: event with the id {event_id} does not exist!'
    else:
        result = _validate_event(name, event_date)
        if isinstance(result, str):
            return result
        else:
            name, event_date = result

            check_event_exist = _check_event_exists_by_event_name_date(name, event_date)
            if 'SUCCESS' in check_event_exist:  # event does not exist, so change the habit_name and event_date
                query = "UPDATE events set habit_name=?, event_date=? WHERE event_id=?"
                parameters = (name, event_date, event_id)
                _execute_query(query, parameters)
            else:
                return check_event_exist

        return f'event {event_id} for habit {name} has been updated!'


def delete_event(event_id: str):
    """Delete a habit event with the given event_id existing in the database.

    :params: event_id: event_id of the habit event to be deleted
    :return: Returns a message that the habit event was successfully deleted
        from the sqlite3 database or that no habit event was found matching the
        supplied event_id
    """
    if_exist = get_event(event_id)
    if 'ERROR' in if_exist:
        return f'ERROR: event with the event_id {event_id} does not exist!'
    else:
        query = "DELETE FROM events WHERE event_id=?"
        parameter = (event_id,)
        _execute_query(query, parameter)
        return f'event {event_id} has been deleted!'


def delete_events(name: str):
    """Delete all habit events for the named habit existing in the database.

    :params: name: name of the habit whose events are to be deleted
    :return: Returns a message that the habit events were successfully deleted
        from the sqlite3 database or that no habit event was found for the
        supplied habit name
    """
    if_exist = get_events(name)
    if 'ERROR' in if_exist:
        return f'ERROR: event records for habit {name} does not exist!'
    else:
        query = "DELETE FROM events WHERE habit_name=?"
        parameter = (name.upper(), )
        return _execute_query(query, parameter)
        # return f'event records for habit {name} have been deleted!'
