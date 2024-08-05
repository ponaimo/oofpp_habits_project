import questionary
from db import create_data_storage
from counter import Counter
from analyse import calculate_all_counters, get_all_habits, get_habits_periodically, habit_with_longest_streak


def cli():
    create_data_storage()
    stop = False
    while not stop:
        choice = questionary.select(
           'What would you like to do?',
           choices=['Add Habit', 'View Habits', 'Add Event', 'View Events', 'Analyze', 'Edit', 'Delete', 'Exit']).ask()
        if choice == 'Add Habit':
            name = questionary.text('What is the name of your Habit?').ask()
            desc = questionary.text('Give brief description of Habit').ask()
            start = questionary.text('Specify Habit start date, ignore if date is today eg YYYY-MM-DD hh:mm:ss AM'
                                     ).ask()
            period = questionary.select('How often would you perform this habit?',
                                        choices=['Daily', 'Weekly']).ask()
            cut_style = questionary.select(
                'Is this habit time sensitive? Indicate time pattern',
                choices=['IGNORE', 'ON', 'BEFORE', 'AFTER']).ask()
            cut_off_time = '00:00:00'
            if not (cut_style == 'IGNORE'):
                cut_off_time = questionary.text('State time for habit eg 01:40:57 AM').ask()
            my_counter = Counter(name, desc, start, period, cut_style, cut_off_time)

            print(my_counter.add_habit())
        elif choice == 'View Habits':
            print(get_all_habits())
        elif choice == 'Add Event':
            name = questionary.text('What is the name of your Habit?').ask()
            event_date = questionary.text('Specify event date,ignore if datetime is now eg YYYY-MM-DD hh:mm:ss AM'
                                          ).ask()
            my_counter = Counter(name)
            print(my_counter.add_event(event_date))
        elif choice == 'View Events':
            habit_name = questionary.text('Provide name of habit').ask()
            my_counter = Counter(habit_name)
            print(my_counter.get_events())
        elif choice == 'Analyze':
            my_pick = questionary.select('Which analysis would you like to see?',
                                         choices=['All Habits with same Periodicity', 'All Habits Streaks',
                                                  'Any Habit Streak', 'Longest Streak Habit']).ask()
            if my_pick == 'All Habits with same Periodicity':
                frequency = questionary.select(
                    'Select habit periodicity to view',
                    choices=['Daily', 'Weekly']
                ).ask()
                print(get_habits_periodically(frequency))
            elif my_pick == 'Any Habit Streak':
                habit_name = questionary.text('Provide name of habit you want to analyze').ask()
                my_counter = Counter(habit_name)
                my_counter.calculate_streak()
                print(my_counter.__str__())
            elif my_pick == 'All Habits Streaks':
                print(calculate_all_counters())
            elif my_pick == 'Longest Streak Habit':
                print(habit_with_longest_streak())
            else:
                print(f'Unknown request {my_pick}! Please check the spellings.')
        elif choice == 'Edit':
            correction = questionary.select(
                'What would you like to edit?',
                choices=['Habit', 'Event']
                ).ask()
            if correction == 'Habit':
                take = questionary.select('What would you like to do', choices=['Edit Habit', 'Stop Habit']
                                          ).ask()
                if take == 'Edit Habit':
                    habit_name = questionary.text('Provide habit name.').ask()
                    print("""All other parameters are optional. Any parameter you do not wish to edit, 
                          press Enter to continue.""")
                    desc = questionary.text('Give brief description of Habit').ask()
                    start = questionary.text('Specify Habit start date, eg YYYY-MM-DD hh:mm:ss AM').ask()
                    period = questionary.select('How often would you be performing this habit?',
                                                choices=['Daily', 'Weekly']).ask()
                    cut_style = questionary.select('Is this habit time sensitive? Choose pattern',
                                                   choices=['IGNORE', 'ON', 'BEFORE', 'AFTER']).ask()
                    cut_off_time = '00:00:00'
                    if not (cut_style == 'IGNORE'):
                        cut_off_time = questionary.text('State time for habit eg 01:40:57 AM').ask()
                    my_counter = Counter(habit_name, desc, start, period, cut_style, cut_off_time)

                    print(my_counter.update_my_habit(desc, start, period, cut_style, cut_off_time))

                elif take == 'Stop Habit':
                    habit_name = questionary.text('Provide habit name to be stopped.').ask()

                    serious = questionary.select("""This habit would be stopped and no longer monitored by HTP. 
                                    Do you wish to continue?""", choices=['Yes', 'No']).ask()
                    if serious == 'Yes':
                        my_counter = Counter(habit_name, '', '', '', '',
                                             '', '')

                        print(my_counter.stop_my_habit())
                    else:
                        print('Habit stoping action was discontinued by user!')
                else:
                    print(f'Unknown habit edit command {take}! Check spellings')
            elif correction == 'Event':
                print("""You would need the event_id to be able to edit an event. Go back and select View Events,then 
                copy the long event_id and paste it when asked.""")
                habit_name = questionary.text('Provide habit name.').ask()
                event_id = questionary.text('Provide event_id.').ask()
                event_date = questionary.text("""Provide event date, if you want to edit the date eg YYYY-MM-DD 
                hh:mm:ss AM or ignore if not""").ask()
                my_counter = Counter(habit_name)
                print(my_counter.update_my_event(event_id, habit_name, event_date))
            else:
                print(f'Unknown edit command {correction}! Check spellings')

        elif choice == 'Delete':
            clean = questionary.select(
                'What would you like to delete?',
                choices=['Habit', 'Event']
                ).ask()
            if clean == 'Habit':
                serious = questionary.select("""All events associated with this habit will also be deleted. 
                Do you wish to continue?""", choices=['Yes', 'No']).ask()
                if serious == 'Yes':
                    habit_name = questionary.text('Provide habit name.').ask()
                    my_counter = Counter(habit_name)
                    print(my_counter.delete_my_habit_plus_events())
                else:
                    print('Habit deleting was discontinued by user!')
            elif clean == 'Event':
                print("""You would need the event_id to be able to delete an event. Go back and select View Events, 
                                                          then copy the long event_id and paste it when asked.""")
                habit_name = questionary.text('Provide habit name.').ask()
                event_id = questionary.text('Provide event_id.').ask()
                my_counter = Counter(habit_name)
                print(my_counter.delete_my_event(event_id))
            else:
                print(f'Unknown delete command {clean}! Check spellings')
        elif choice == 'Exit':
            print('Thanks for using Habit Tracker Plus!')
            stop = True
        else:
            print(f'Unknown request {choice}! Please check the spellings.')


if __name__ == "__main__":
    cli()
