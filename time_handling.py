"""Functions to deal with time, mainly converting 24H clock format to seconds"""

import time

def time_to_seconds(time_24h: str) -> int:
    """
    Converts a given time with the format HH:MM (24 hour clock) into its
    number of seconds relative to 00:00

    Parameters:
        time_24h(str): a time with format HH:MM

    Returns:
        seconds(int): an integer representing seconds
    """
    #check validity of given time
    if len(time_24h.split(':')) != 2:
        print('Incorrect format. Argument must be formatted as HH:MM')
        return None
    return 60*60*(int(time_24h.split(':')[0])) + 60*(int(time_24h.split(':')[1]))

def current_time_func() -> str:
    """
    returns the current time in a HH:MM format

    Parameters:
        None

    Returns:
        time(str): The current time in the format HH:MM
    """
    #get current hour as a string
    hour = str(time.gmtime().tm_hour)
    if len(hour) == 1:
        hour = f"0{hour}"

    #get current minute as a string
    minute = str(time.gmtime().tm_min)
    if len(minute) == 1:
        minute = f"0{minute}"

    return f"{hour}:{minute}"

def update_interval_func(scheduled_time: str) -> int:
    """
    Calculates the number of seconds between the current time and a given time

    Parameters:
        Scheduled_time(str): a given time in the format HH:MM

    returns:
        update_interval(int): an integer representing the difference between scheduled_time
                              and the current time in seconds
    """
    current_time = time_to_seconds(current_time_func())
    scheduled_time = time_to_seconds(scheduled_time)
    update_interval = scheduled_time - current_time

    if update_interval > 0:
        return update_interval
    #if update interval = 0, scheduled time = given time, so
    if update_interval == 0:
        return 1
    #update interval is negative, scheduled time was set as a time which already passed today.
    #Add 24H to set it for tomorrow at the scheduled time
    return update_interval + time_to_seconds("24:00")
