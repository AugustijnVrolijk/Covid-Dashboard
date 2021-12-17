CONTENTS OF THIS FILE
---------------------

 * Introduction
 * Requirements
 * Installation
 * Configuration



INTRODUCTION
------------

The six accompanying files including: 

templates\index.html
config.json
covid_data_handler.py
covid_news_handling.py
time_handling.py
ui.py


are part of a covid 19 dashboard customizable for the UK.

This dashboard was created in accordance to a university project specification and 
therefore has limitations to functionality, as well as efficiency.

The dashboard shows local as well as national statistics for covid-19. As well as relevant
news articles originating from the UK and in english. The dashboard includes an update 
system to refresh the covid-19 data and news articles.

Many of the characteristics can be changed through the config.json file. 
These characteristics may include parameters such as the language to sort for when 
requesting news articles.

All the files can be found at: https://github.com/funnycones/Covid-Dashboard.git

Once installed the dashboard can be started by running ui.py
Once the program is running, the website can be found at:
http://127.0.0.1:5000/index



REQUIREMENTS
------------

For the dashboard to work your machine must have python 3.9 installed. Earlier versions
of python might be compatible.

To be able to run the program you must have a folder containing:

All 4 .py files listed in the introduction
The config file named config.json
index.html in a folder called templates



Installation
------------

For the python files to function, certain libraries must be installed.
These include:

uk-covid19
newsapi-python

To install uk-covid19, please run:

> pip install uk-covid19

Earlier versions can be installed using:

> python -m pip install uk-covid19


To install newsapi-python, please run:

> pip install newsapi-python

Furthermore a newsAPI key is necessary. You can easily get an newsAPI key on the following
site: https://newsapi.org/

Once you have an API key you will need to copy it into the config.json file.
This file can easily be edited using any text editor such as notepad.
Insert the API key between the quotation marks corresponding to "covidnews_API_key"



Configuration
------------

Configuration is easily done through the config file by changing the value
corresponding to the parameter you want to change.

i.e if you no longer want to have your news cached, change:

	"Cache_news": "true"
	
		to

	"Cache_news": "false"

Make certain to only change the value and not the parameter.
Valid values to certain parameters can be found at https://newsapi.org/

The image displayed as well as favicon can be changed through the \static\images\"image".jpg path. 
Make certain that any images you want to be displayed are in the file location listed above.


Further configuration:

The dashboard website code can be changed at templates\index.html.
Parameters for the displayed covid data can be changed in the covid_data_handler.py file

More info for valid parameters for this file can be found at:

https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/
https://coronavirus.data.gov.uk/details/developers-guide/main-api

