from pymongo import MongoClient

# temporary or testing imports
import os.path #Can be removed once we set up the db
#import ipdb

from boxscore_scraper import *
#from roster_scraper import *

class Scraper(object):

    def __init__(self,debug=False):
        self.debug=debug
        try:
            self.client = MongoClient()
        except:
            print("MongoDB: Connection refused")
        self.box_scraper = BoxScoreScraper(self.client)
        self.box_scraper.debug = True
        #self.roster_scraper = RosterScraper(self.client)
        
    
    def scrape(self, year=2015):
        self.box_scraper.scrape(year=year)
        #self.roster_scraper.Scrape()
