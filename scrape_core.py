from bs4 import BeautifulSoup
from tabulate import tabulate
from urllib.request import urlopen

# temporary or testing imports
import os.path #Can be removed once we set up the db
import re
import json
from pymongo import MongoClient
import ipdb

class Scrape(object):

    def __init__(self,year=None,debug=False):
        self.year = year
        self.base_url = 'http://www.basketball-reference.com'
        self.debug=debug
        try:
            self.client = MongoClient()
        except:
            print("MongoDB: Connection refused")
        
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
        files = os.listdir(PATH)
        exists = False
        for f in files:
            if ID in f:
                exists = True
        return exists
    
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
            'basic' or 'advanced', pertaining to the field_type of data obtained

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

        # Check for game data existence in db
        gametag = self.game_url.split('/')[-1].strip('.html')
        exists = self._ID_exists_in_DB(gametag+field_type)
        # Obtain the html if game doesn't exist
        if exists is False:
            html = urlopen(self.game_url).read()
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
        else:
            print("Game {} already exists in db. Skipping web-scraping phase...".format(gametag))
            return self.boxscore_data, gametag

    def display_boxscore(self,boxscore_data):
        """
        A public function which prints the data table for a given boxscore dictionary.

        Parameters
        ----------
        boxscore_data : dict
            A dictionary of data for every player. Basic/Advanced field_type is learned
        from the input.

        Returns
        -------
        """
        
        data = []
        field_type = None
        
        # headers
        if len(boxscore_data[[i for i in boxscore_data.keys()][0]]) == 20:
            data.append(["Name"] + self.data_fields['basic'])
            field_type='basic'
        elif len(boxscore_data[[i for i in boxscore_data.keys()][0]]) == 13:
            data.append(["Name"] + self.data_fields['advanced'])
            field_type='advanced'
        else:
            "ERROR MESSAGE HERE"

        # data
        for player in self.boxscore_data:
            row = [player]
            for k in self.data_fields['{}'.format(field_type)]:
                row.append(self.boxscore_data[player][k])
            data.append(row)
        print(tabulate(data))

    def _dump_gamedata_to_json(self,boxscore_data,gametag):
        """
        A private function which writes all game data to a json file, where 
        the filename is the gametag. 
        ** Currently dumps json files in directory called 'data' on Desktop 
        ** (../../), two directories up from git directory.

        Parameters
        ----------
        boxscore_data : dict
            A dictionary of data for every player. Basic/Advanced field_type is learned
            from the input.
        gametag : str
            Unique game id number.
        """
        
        # Checks for the empty dictionary, which is an indication that the data have
        # not been retrieved from the web; it already exists locally.
        field_type = None
        if len(boxscore_data.keys()) == 0:
            if self.debug is True:
                print("Game {} already exists in db. Skipping storage phase...".format(gametag))
            return
        # Figures out if field_type is 'basic' or 'advanced'        
        if len(boxscore_data[[i for i in boxscore_data.keys()][0]]) == 20:
            field_type='basic'
        elif len(boxscore_data[[i for i in boxscore_data.keys()][0]]) == 13:
            field_type='advanced'
        else:
            print("ERROR: Neither basic nor advanced data is being requested...")

        # Check to see if game_data exists in database
        exists = self._ID_exists_in_DB(gametag+field_type)
        if exists is False:
            with open ('../../data/'+gametag+field_type+'.json','w') as f:
                json.dump(boxscore_data, f)
            if self.debug is True:
                print("Wrote game {} out to file...".format(gametag))
        else:
            if self.debug is True:
                print("Game {} already exists in db. Skipping storage phase...".format(gametag))

    def _write_to_mongodb(self):
        self.db = self.client.game_data
        self.posts = self.db.posts
        
        ipdb.set_trace()
        
if __name__ == "__main__":
    
    # Test #1: Scrape 2014, and choose the first game.
    # Get boxscore, and print table to terminal. Then
    # dump game data to json file (currently on Desktop).
    '''
    s2014 = Scrape(year=2014)
    links2014 = s2014._get_game_urls_for_season()
    boxscore_data,gametag = s2014._get_boxscore(links2014[0],field_type='basic')
    s2014.display_boxscore(boxscore_data)
    s2014._dump_gamedata_to_json(boxscore_data,gametag)
    '''

    # Test #2: Store game data for all basketball games
    # for 2013 season. Check to see if any have been
    # dumped to json files previously. Eventually, check
    # against database rather than json file.
    #s2013 = Scrape(year=2013,debug=True)
    '''
    links2013 = s2013._get_game_urls_for_season()
    for li in links2013:
        boxscore_data,gametag = s2013._get_boxscore(li,field_type='advanced')
        s2013._dump_gamedata_to_json(boxscore_data,gametag)
        boxscore_data,gametag = s2013._get_boxscore(li,field_type='basic')
        s2013._dump_gamedata_to_json(boxscore_data,gametag)
    '''
