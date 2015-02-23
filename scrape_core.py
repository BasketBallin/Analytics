from bs4 import BeautifulSoup
from tabulate import tabulate
from urllib.request import urlopen

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
        html = urlopen(self.game_url).read()        
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

    def _get_boxscore(self,game_url,field_type='basic'):
        """
        Private function which retrieves all data for a given game_url.

        Parameters
        ----------
        game_url : str
            The basketball-reference.com game url.
        field_type : str
            'basic' or 'advanced', pertaining to the type of data obtained

        Returns
        -------
        boxscore_data : dict
            Boxscore dictionary of basic or advanced data fields for all players
            for specified game.
        gametag : str
            Unique game id number.

        """
        
        # Make sure that a game has been specified
        self.game_url = game_url
        self.boxscore_data = {}
        assert self.game_url is not None, "Must specify a game."

        # Setting up dictionary storage structure
        self.data_fields = {'basic':['MP','FG','FGA','FG%','3P','3PA','3P%',
                                'FT','FTA','FT%','ORB','DRB','TRB','AST',
                                'STL','BLK','TOV','PF','PTS','+/-'],
                       'advanced':['MP','TS%','eFG%','ORB%','DRB%','TRB%',
                                   'AST%','STL%','BLK%','TOV%','USG%','ORtg',
                                   'DRtg']}

        # Obtain the html
        html = urlopen(self.game_url).read()
        gametag = self.game_url.split('/')[-1].strip('.html')
        soup = BeautifulSoup(html,'html.parser')
        
        fields = self.data_fields['{}'.format(field_type)]
        
        # Get table from html
        tables = soup.findAll('table', id=re.compile(field_type))
        tables = [t.find('tbody') for t in tables]
    
        for t in tables:
            data = t.findAll('tr')
            for player in data:
                if player['class'][0] == '':
                    pdata = player.findAll('td')
                    name = pdata[0].string
                    # is this sufficient to always determine if
                    # the player wasn't on the bench?
                    if len(pdata) > 2: 
                        tmp = self.boxscore_data.get(name, {})
                        for i,k in enumerate(fields):
                            if pdata[i] == None:
                                pdata[i] = 'None'
                            tmp[k] = pdata[i+1].string
                        self.boxscore_data[name] = tmp

        return self.boxscore_data, gametag

    def display_boxscore(self,boxscore_data):
        """
        A public function which prints the data table for a given boxscore dictionary.

        Parameters
        ----------
        boxscore_data : dict
            A dictionary of data for every player. Basic/Advanced type is learned
        from the input.

        Returns
        -------
        """
        
        data = []
        type = None
        
        # headers
        if len(boxscore_data[[i for i in boxscore_data.keys()][0]]) == 20:
            data.append(["Name"] + self.data_fields['basic'])
            type='basic'
        elif len(boxscore_data[[i for i in boxscore_data.keys()][0]]) == 13:
            data.append(["Name"] + self.data_fields['advanced'])
            type='advanced'
        else:
            "ERROR MESSAGE HERE"

        # data
        for player in self.boxscore_data:
            row = [player]
            for k in self.data_fields['{}'.format(type)]:
                row.append(self.boxscore_data[player][k])
            data.append(row)
        print(tabulate(data))

        
        
if __name__ == "__main__":
    # Test #1
    s2014 = Scrape(year=2014)
    links2014 = s2014._get_game_urls_for_season()
    boxscore_data,gametag = s2014._get_boxscore(links2014[0],field_type='basic')
    s2014.display_boxscore(boxscore_data)
    
