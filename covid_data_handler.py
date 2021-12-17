"""This file deals with requesting covid data from Cov19API"""

import sched
import time
from typing import List, Tuple, Dict
from uk_covid19 import Cov19API

#initializing scheduler object from sched library
s = sched.scheduler(time.time, time.sleep)

def parse_csv_data(csv_filename: str) -> List[str]:
    """
    converts a .csv file into a list of strings

    Paramters:
        csv_filename(str): the .csv file to be converted, this should be the filename or
                           relative path given as a string

    Returns:
        csv_data(list): a list of strings, where each string is a line of the .csv file
    """
    #check that the given csv file is valid
    if not isinstance(csv_filename, str):
        csv_filename = str(csv_filename)
    if csv_filename[-4:] != ".csv":
        csv_filename = csv_filename + ".csv"

    #append each line of the csv to a list
    csv_data = []
    with open(csv_filename, "r", encoding="utf-8") as csv_file:
        for line in csv_file:
            csv_data.append(line.strip())
        return csv_data


def process_covid_csv_data(covid_csv_data: List[str]) -> Tuple[int, int, int]:
    """
    sorts through a list of strings to find relevant data

    Parameters:
        covid_csv_data: a list of strings, where each string represents a row from a data set

    Returns:
        int(last7days_cases): the sum of cases from the last 7 days
        int(current_hospital_cases): the most recent figure for hospital cases
        int(total_deaths): the most recent figure for total deaths
    """
    #check that the first string, representing the parameters of the data set contains some data
    parameter_list = covid_csv_data[0].split(",")
    if len(parameter_list) <= 1:
        return 0, 0, 0

    current_hospital_cases = 0
    total_deaths = 0
    last7days_cases = 0
    current_hospital_cases_index = parameter_list.index("hospitalCases")
    last7days_cases_index = parameter_list.index("newCasesBySpecimenDate")
    total_deaths_index = parameter_list.index("cumDailyNsoDeathsByDeathDate")
    count = 0

    for i in covid_csv_data[1:-1]:
        line = i.split(",")
        #checks if total_deaths is an int -> has it been changed? and whether there is data present
        if isinstance(total_deaths, int) and line[total_deaths_index] != "":
            total_deaths = line[total_deaths_index]
        if isinstance(current_hospital_cases, int) and line[current_hospital_cases_index] != "":
            current_hospital_cases = line[current_hospital_cases_index]
        #repeats 7 times, between count 1 & 8, as each row correpsonds to a day. gives the sum of
        #cases for the last week
        if 8 > count >= 1:
            last7days_cases += int(line[last7days_cases_index])
            count += 1
        #starts count if there is data in the last7days_cases column -> ignore the first entry
        #as its incomplete data for the day
        elif count == 0 and line[last7days_cases_index] != "":
            count = 1
        #breaks once all params have been filled
        elif count == 8:
            if not isinstance(total_deaths, int) and not isinstance(current_hospital_cases, int):
                break

    return int(last7days_cases), int(current_hospital_cases), int(total_deaths)

def covid_API_request(location: str = "Exeter", location_type:str = "ltla") -> Dict[str, int]:
    """
    Requests a .csv with covid data pertaining to a specified location, then process this .csv file
    using parse_csv_data and process_covid_csv_data to return a dictionary with relevant data

    Parameters:
        location: The name of the area in which you are interested as a string. First letter must be
                  a capital apart for countires
        location_type: The type of location your location is as a string. More info can be found on
                       the Cov19API website:
                       https://coronavirus.data.gov.uk/details/developers-guide/main-api

    Returns:
        final_data(dictionary): returns dict with relevant data extracted from the requested CSV
    """
    valid_location_types = ["overview", "nation", "region", "nhsRegion", "utla", "ltla"]
    #check validity of given parameters
    if not isinstance(location_type, str):
        location_type = str(location_type)
    if not isinstance(location, str):
        location = str(location)
    if location_type not in valid_location_types:
        return print(f"{location_type} is invalid, valid location types are: {str(valid_location_types)}")

    #URL sent for the .csv request
    location_filter = [f"areaType={location_type}", f"areaName={location}"]

    #using the Cov19API tool to request data
    data = {"date": "date",
            "areaName": "areaName",
            "newCasesBySpecimenDate": "newCasesBySpecimenDate",
            "hospitalCases": "hospitalCases",
            "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate"}
    api = Cov19API(filters=location_filter, structure=data)
    data_filename = "data.csv"
    api.get_csv(save_as=data_filename)

    #process & format csv to get final data
    last7days_cases, hospital_cases, deaths = process_covid_csv_data(parse_csv_data(data_filename))
    final_data = {"last7days_cases" : last7days_cases,
                  "hospital_cases" : hospital_cases,
                  "deaths" : deaths}
    return final_data

def schedule_covid_updates(update_name:None, update_interval:int, arguments:Tuple[str]) -> None:
    """
    Scheduler for covid_API_request using the Sched library
    function is useless, never called, needed for coursework...
    check schedule_updates in UI.py

    Parameters:
        update_name: Name of the function to be ran
        update_interval: Number of seconds the scheduler should wait before running the function
        arguments: A tuple containing any arguments the update_name function would need in order
                   to run, if only 1 argument is given make sure it's a tuple ending with a comma

        Returns:
            None
    """
    #add update to scheduler & run it
    s.enter(update_interval, 1, update_name, arguments)
    s.run()
