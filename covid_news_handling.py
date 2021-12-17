"""This file deals with requesting article from https://newsapi.org/"""

import json
from typing import Dict
import requests

def news_API_request(covid_terms:str = "Covid COVID-19 coronavirus") -> Dict[str, str]:
    """
    requests articles from https://newsapi.org/ given certain parameters

    hidden parameters include:
        API_key(str): API key needed to request articles from the newsapi
                      more info on getting an API key in README.txt
        country(str): get news articles from a certain country
        language(str): get news articles in a certain language

    parameters:
        covid_terms(str):keyword/keywords to search for articles containing them

    returns:
        news(dict):dictionary containing articles in title:content format
    """
    news = {}
    if not isinstance(covid_terms, str):
        covid_terms = str(covid_terms)

    #retrieve hidden parameters from config file
    with open("config.json", "r", encoding="utf-8") as json_file:
        config = json.load(json_file)
        news_API_request_terms = config["news_API_request_terms"]
        API_key = news_API_request_terms["covidnews_API_key"]
        url_args = news_API_request_terms["url_args"]
        country = url_args["country"]
        language = url_args["language"]
        covid_terms = url_args["Covid_terms"]

    #split in case given covid_terms has multiple keywords in it
    covid_term = covid_terms.split()
    for term in covid_term:
        url = ('https://newsapi.org/v2/top-headlines?'
               'country=' + country + '&'
               'language=' + language + '&'
               'q=' + term + '&'
               'apiKey=' + API_key)

        #use request library from newsapi to access articles
        response = requests.get(url)
        requested_articles = response.json()
        #the requested json file has a specific structure, to see what parameters
        #are given, check https://newsapi.org/
        if requested_articles["status"] == "error":
            news["News API request failed"] = requested_articles["message"]

        else:
            articles = requested_articles["articles"]
            for article in articles:
                news[article["title"]] = article["content"]

    return news

def update_news(terms:str = "Covid COVID-19 Coronavirus") -> None:
    """
    function needed for coursework... updating news can be achieved from UI.py

    Parameters:
        terms(str): covid terms to pass onto news_API_request

    returns:
        None
    """
    news_API_request(terms)
