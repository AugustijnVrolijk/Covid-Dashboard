"""Main program oversees creating a webpage & updating it"""

import json
import sched
import time
import os
from typing import Dict, Callable
from flask import Flask, render_template, request
from covid_news_handling import news_API_request
from covid_data_handler import covid_API_request
from time_handling import update_interval_func, current_time_func

#initializing app from flask library
app = Flask(__name__)
#initializing scheduler object from sched library
s = sched.scheduler(time.time, time.sleep)

def update_config(data:Dict) -> None:
    """
    Rewrites given data to the config file

    Parameters:
        data: Dictionary formatted as a .json file. This dictionary will
              overwrite the current config.json file

    Returns:
        None
    """
    with open("config.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file)

def update_news(repeat: bool, label: str):
    """
    calls for news_API_request() from covid_news_handling, then sorts
    through the returned dictionary to add new articles to local news dictionary

    parameters:
        Repeat(bool): whether the update should repeat after running
        Label(str): name of the update calling this function
                   (used to cancel the update)

    returns:
        None
    """
    #request news from news_api_request
    new_news = news_API_request()
    #add news to master dict if it has not previously been removed
    for title, article in new_news.items():
        if title not in DELETED_NEWS:
            NEWS[title] = article

    #update news dictionary in config file if caching is enabled
    if CACHE_NEWS:
        with open("config.json", "r", encoding="utf-8") as json_file:
            config = json.load(json_file)
            config["News_articles"] = NEWS
        update_config(config)

    #schedule new update if repeat is true,
    #86400 -> number of seconds in a day, make update happen a day from now
    #1, priority of update, default as 1
    #update_news function to be ran once timer passes
    #(Repeat, Label) arguments to pass to the function
    if repeat:
        s.enter(86400, 1, update_news, (repeat, label))
    else:
        #update config scheduled updates dictionary to remove the update (it ran)
        if CACHE_UPDATES:
            with open("config.json", "r", encoding="utf-8") as json_file:
                config_file = json.load(json_file)
                del config_file["Scheduled_updates"][label]
            update_config(config_file)

        del SCHEDULED_UPDATES[label]

def remove_news_article(title:str) -> None:
    """
    remove a news article from the dictionary of articles to be shown

    parameters:
        title(str): title of the article to be removed

    returns:
        None
    """

    #delete title from global list, add it to deleted news so it doesn't get re-added
    DELETED_NEWS.append(title)
    del NEWS[title]

    #update config news dictionaries to be up to date
    if CACHE_NEWS:
        with open("config.json", "r", encoding="utf-8") as json_file:
            config = json.load(json_file)
            config["News_articles"] = NEWS
            config["Deleted_news_articles"] = DELETED_NEWS
        update_config(config)


def update_covid_data(repeat: bool, label: str) -> None:
    """
    calls for covid_API_request to update covid data

    parameters:
        Repeat(bool): whether the update should repeat once ran
        Label(str): name of the update calling on this function

    returns:
        None
    """
    LOCAL_COVID_API = covid_API_request("Exeter", "ltla")
    NATIONAL_COVID_API = covid_API_request("England", "nation")

    #schedule new update if repeat, parameters explained in update_news()
    if repeat:
        s.enter(86400, 1, update_covid_data, (repeat, label))
    #deletes update from master dictionary(it ran)
    else:
        #updates SCHEDULED_UPDATES dictionary in config file
        if CACHE_UPDATES:
            with open("config.json", "r", encoding="utf-8") as json_file:
                config_file = json.load(json_file)
                del config_file["Scheduled_updates"][label]
            update_config(config_file)
        del SCHEDULED_UPDATES[label]


def schedule_update(label:str, update_time:str, update_func: Callable[bool, str], repeat: bool = False) -> None:
    """
    uses the sched library to add a scheduled update, triggered by the website

    Parameters:
        Label(str): Name of the update to be scheduled
        update_time(str): Time at which the update should run, 24h clock format
        update_func(function): function to be triggered by the update
        repeat(bool): boolean representing whether the update should repeat once it runs

    returns:
        None
    """
    #check if label already exists, if so add (number) to the end of it in order to make it unique
    if label in SCHEDULED_UPDATES.keys():
        label_temp = str(label)
        count = 1
        while True:
            count += 1
            label = f"{label_temp}({count})"
            if label not in SCHEDULED_UPDATES.keys():
                break

    #update scheduled updates in config file
    if CACHE_UPDATES:
        with open("config.json", "r", encoding="utf-8") as json_file:
            config = json.load(json_file)
            config["Scheduled_updates"][label] = "{} to {} at {}".format((str(update_func).split(" "))[1],"repeat" if repeat else "occur", update_time)
        update_config(config)

    #add scheduled update to sched module /master scheduled updates list
    SCHEDULED_UPDATES[label] = "{} to {} at {}".format((str(update_func).split(" "))[1],"repeat" if repeat else "occur", update_time)
    s.enter(update_interval_func(update_time), 1, update_func, (repeat, label))

def cancel_scheduled_update(label:str) -> None:
    """
    cancels an update in the scheduler object given its name

    parameters:
        label(str): name of the update to be cancelled

    returns:
        None
    """
    #iterate through scheduler object queue to find which update the label refers to
    for event in s.queue:
        if label == str(event[3][1]):
            #deletes update from config file
            if CACHE_UPDATES:
                with open("config.json", "r", encoding="utf-8") as json_file:
                    config_file = json.load(json_file)
                    del config_file["Scheduled_updates"][label]
                update_config(config_file)

            #deletes/cancel update
            del SCHEDULED_UPDATES[label]
            s.cancel(event)
            break

#when the website is refreshed with /index at the end of the url, triggers this function
@app.route('/index')
def index():
    """
    main function, calls upon Scheduled_updates if requested by website
    and returns values to website

    parameters:
        none

    returns:
        render_template(dict): parameters to be given to html code
    """
    #get parameters from url i.e. if url: /index?update=&two=hello&news=news
    #it will assign update_label as "hello" and check_update_news_articles as "news"
    #remove_update returns title of the update to be removed
    #remove_news returns title of article to be removed
    #check_update_covid_data returns "covid-data" if triggered
    #check_update_news_articles returns "news" if triggered
    remove_update = request.args.get("update_item")
    remove_news = request.args.get("notif")
    update_time = request.args.get("update")
    repeat_update = request.args.get("repeat")
    update_label = request.args.get("two")
    check_update_covid_data = request.args.get("covid-data")
    check_update_news_articles = request.args.get("news")

    #run any scheduled updates which are due
    #keep at the front of the function, if this is triggered after adding new updates
    #will cause problems in cases where no time has been specified and repeat is true
    s.run(blocking=False)

    #if certain param has been assigned something (not none)
    if remove_update:
        cancel_scheduled_update(remove_update)
    if remove_news:
        remove_news_article(remove_news)
    #assign current time if none has been assigned
    if not update_time:
        update_time = current_time_func()
    repeat = bool(repeat_update)

    #triggers update if update name has been given - then checks which update to trigger
    if update_label:
        if check_update_covid_data:
            schedule_update(update_label, update_time, update_covid_data, repeat)
        if check_update_news_articles:
            schedule_update(update_label, update_time, update_news, repeat)

    #converts scheduled updates & news dictionaries into lists of dictionaries
    updates = []
    for key, value in SCHEDULED_UPDATES.items():
        updates.append({"title":key,"content":value})
    news_list = []
    for key, value in NEWS.items():
        news_list.append({"title":key,"content":value})

    #returns values to assignable objects in html code in templates/index
    return render_template('index.html',
                           title='Daily update',
                           updates=updates,
                           news_articles=news_list,
                           location="Exeter",
                           nation_location="England",
                           local_7day_infections=LOCAL_COVID_API["last7days_cases"],
                           national_7day_infections=NATIONAL_COVID_API["last7days_cases"],
                           hospital_cases=NATIONAL_COVID_API["hospital_cases"],
                           deaths_total=NATIONAL_COVID_API["deaths"],
                           image="Shrek-swamp-1.jpg",
                           favicon="static/images/onion.ico")

def startup() -> None:
    """
    defines certain global variables from config file & updates scheduler/news from config file

    parameters:
        None

    returns:
        None
    """
    global NEWS, DELETED_NEWS, LOCAL_COVID_API, NATIONAL_COVID_API
    global CACHE_UPDATES, CACHE_NEWS, SCHEDULED_UPDATES

    #get local & national covid data from covid_API_request()
    LOCAL_COVID_API = covid_API_request()
    NATIONAL_COVID_API = covid_API_request("england", "nation")

    #updates parameters including news & scheduled updates from config file
    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as json_config_file:
            config_file = json.load(json_config_file)

            if config_file["Cache_updates"].lower() == "false":
                CACHE_UPDATES = False
                SCHEDULED_UPDATES = {}
                config_file["Scheduled_updates"] = {}
            else:
                CACHE_UPDATES = True
                SCHEDULED_UPDATES = config_file["Scheduled_updates"]
                #iterates through SCHEDULED_UPDATES dictionary to re-schedule existing updates
                for key, value in config_file["Scheduled_updates"].items():
                    #key is the label
                    #value is in format: "{function} to {repeat} at {time}"
                    values = value.split(" ")
                    if values[0] == "update_covid_data":
                        func = update_covid_data
                    else:
                        func = update_news
                    if values[2] == "repeat":
                        repeat = True
                    else:
                        repeat = False
                    s.enter(update_interval_func(values[4]), 1, func, (repeat, key, values[4]))

            if config_file["Cache_news"].lower() == "false":
                CACHE_NEWS = False
                config_file["News_articles"] = []
                config_file["Deleted_news_articles"] = []
                DELETED_NEWS = []
                NEWS = news_API_request()
            else:
                CACHE_NEWS = True
                NEWS = config_file["News_articles"]
                DELETED_NEWS = config_file["Deleted_news_articles"]
                update_news(False, "", "")

        #update config file & initialise website
        update_config(config_file)

    else:
        print("Error: No config file found")

if __name__ == '__main__':
    startup()
    app.run()
