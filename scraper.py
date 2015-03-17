from pymongo import MongoClient

import time

# temporary or testing imports
import os.path #Can be removed once we set up the db
#import ipdb

from boxscore_scraper import *
#from roster_scraper import *

class Scraper(object):

    def __init__(self,debug=False):
        self.debug=debug
        # get current year
        self.current_year = time.localtime().tm_year
        
        # checking is mongodb client is running
        try:
            self.client = MongoClient()
        except:
            print("MongoDB: Connection refused")

        self.box_scraper = BoxScoreScraper(self.client)

        # turning debugging on
        if debug is True:
            self.box_scraper.debug = True
            
        #self.roster_scraper = RosterScraper(self.client)
        
    
    def scrape(self, year=None):
        if year is None:
            year = self.current_year
        self.box_scraper.scrape(year=year)
        #self.roster_scraper.Scrape()
