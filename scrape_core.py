from bs4 import BeautifulSoup
import urllib2
import os.path #Can be removed once we set up the db

class Scrape(object):

    def __init__(self,year=None):
        self.year = year
        self.base_url = 'http://www.basketball-reference.com'

    def _check_game_exists(self, boxscore_link):
        """
        Private function that checks a link against the data we have already downloaded
        """
	#Last part of the link holds the ID.
	game = boxscore_link.split('/')[-1]
	ID = game[:-5]

	#Querry the database to see if this ID already exists
	return self._ID_exists_in_DB(ID)

    def _ID_exists_in_DB(self, ID):
	"""
	Private Function to check if an ID exists in the database for a specific game.

	Right now, we dont have a database, so we are just going to check against the downloaded JSON files, assuming they are stored in ../../data/
	"""
	PATH='../../data/'

	return os.path.exists(PATH+ID+'.json')
    
    def _get_game_urls_for_season(self):
        """
        Private function which returns a list of all game urls for a given season. 
        Currently only implemented for basketball-reference.com.
        """
        
        # Make sure that a season has been specified
        assert self.year is not None, "Must specify an Season."

        # Sets the current game_url 
        self.game_url = self.base_url+"/leagues/NBA_"+str(self.year)+"_games.html"

        # Begin parsing
        html = urllib2.urlopen(self.game_url).read()
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', 'sortable stats_table')
        
        #Get each row of the table
        table = table.find('tbody')
        rows = [row for row in table.findAll('tr')]
	
        #Get the box score link for each row
        boxscore_links = [self.base+row.findAll('td')[1].a['href']
                          for row in rows
                          if row.findAll('td')[1].string == 'Box Score']
	
        return boxscore_links

    
