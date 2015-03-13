# Data Acquisition

This repository contains tools for obtaining NBA team and player data.

### Files:
+ scraper.py : A script to scrape and store all raw nba data products
  from basketball-reference.com. This also handles writing data to a mongodb
  database structure.
+ boxscore_scraper.py: A script which contains the core website scraping
  functionality, specifically for boxscore data.  
+ roster_scraper.py: A script which contains the core website scraping
  functionality, specifically for roster data.

### Examples:
To run, first hop into a terminal and begin mongodb with:

    sudo mongod

Next, run the python scraping tool, by starting up python:

    from scraper import Scraper
    seas2014 = Scraper()
    seas2014.scrape(year=2014)

From here, the script will begin scraping and adding data to the database.
    
