from bs4 import BeautifulSoup
import urllib2
import os.path #Can be removed once we set up the db
import re
import ipdb

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

	Right now, we dont have a database, so we are just going to check against the 
        downloaded JSON files, assuming they are stored in ../../data/ .
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
        boxscore_links = [self.base_url+row.findAll('td')[1].a['href']
                          for row in rows
                          if row.findAll('td')[1].string == 'Box Score']
	
        return boxscore_links

    def _get_boxscore(self,game_url):
        """
        Private function which retrieves all data for a given game_url.
        """
        
        # Make sure that a game has been specified
        self.game_url = game_url
        self.player_data = {}
        assert self.game_url is not None, "Must specify a game."

        # Setting up dictionary storage structure
        data_fields = {'basic':['MP','FG','FGA','FG%','3P','3PA','3P%',
                                'FT','FTA','FT%','ORB','DRB','TRB','AST',
                                'STL','BLK','TOV','PF','PTS','+/-'],
                       'advanced':['MP','TS%','eFG%','ORB%','DRB%','TRB%',
                                   'AST%','STL%','BLK%','TOV%','USG%','ORtg',
                                   'DRtg']}

        # Obtain the html
        html = urllib2.urlopen(self.game_url).read()
        gametag = self.game_url.split('/')[-1].strip('.html')
        soup = BeautifulSoup(html, 'lxml')
        fields_basic = data_fields['basic']
        
        # Get table from html
        tables = soup.findAll('table', id=re.compile('basic'))
        tables = [t.find('tbody') for t in tables]
        for t in tables:
            data = t.findAll('tr')
            for player in data:
                if player['class'][0] == '':
                    pdata = player.findAll('td')
                    name = pdata[0].string
                    #if pdata[1].string != "Did Not Play":
                    if len(pdata) > 2:
                        tmp = player_data.get(name, {})
                        for i,k in enumerate(fields_basic):
                            if pdata[i+1] == None:
                                pdata[i+1] = 'None'
                            tmp[k] = pdata[i+1].string
                        self.player_data[name] = tmp

        
if __name__ == "__main__":
    s2014 = Scrape(year=2014)
    links2014 = s2014._get_game_urls_for_season()
    s2014._get_boxscore(links2014[0])
    ipdb.set_trace()
                            
