from pymongo import MongoClient

from bs4 import BeautifulSoup
from tabulate import tabulate
from urllib.request import urlopen
import re

# temporary imports
import json
import ipdb

class BoxScoreScraper(object):

    def __init__(self, mongo_client=None, debug=False):
        self.client = mongo_client
        self.base_url = 'http://www.basketball-reference.com'
        self.debug = debug

    def _get_game_urls_for_season(self, year=None):
        """
        Private function which returns a list of all game urls for a given season. 
        Currently only implemented for basketball-reference.com.
        """
        
        # Make sure that a season has been specified
        assert year is not None, "Must specify an Season."

        # Sets the current game_url 
        self.game_url = self.base_url+"/leagues/NBA_"+str(year)+"_games.html"

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

    def _get_boxscore(self,game_url):
        """
        Private function which retrieves all data for a given game_url.

        Parameters
        ----------
        game_url : str
            The basketball-reference.com game url.

        Returns
        -------
        boxscore_data : dict
            Boxscore dictionary of basic or advanced data fields for all players
            for specified game.
        gametag : str
            Unique game id number.

        """
        
        # Make sure that a game has been specified
        boxscore_data = {}
        meta_data = {}
        assert game_url is not None, "Must specify a game."

        # Setting up dictionary storage structure
        data_fields = {'basic':['MP','FG','FGA','FG%','3P','3PA','3P%',
                                'FT','FTA','FT%','ORB','DRB','TRB','AST',
                                'STL','BLK','TOV','PF','PTS','+/-'],
                       'advanced':['MP','TS%','eFG%','ORB%','DRB%','TRB%',
                                   'AST%','STL%','BLK%','TOV%','USG%','ORtg',
                                   'DRtg']}

        # Check for game data existence in db
        gametag = game_url.split('/')[-1].strip('.html')
        exists = self._ID_exists_in_DB(gametag)
        # Obtain the html if game doesn't exist
        if exists is False:
            html = urlopen(game_url).read()
            soup = BeautifulSoup(html,'html.parser')
            for field_type in data_fields:
                fields = data_fields['{}'.format(field_type)]
                
                # Get table from html
                tables = soup.findAll('table', id=re.compile(field_type))
                tbodies = [t.find('tbody') for t in tables]
                for i,tab in enumerate(tbodies):
                    tmp_team = tables[i]['id'].split('_')[0]
                    data = tab.findAll('tr')
    
                    for player in data:
                        if player['class'][0] == '':
                            pdata = player.findAll('td')
                            name = pdata[0].string
                            name = name.replace('.','') #No . in keys
                            if len(pdata) > 2: 
                                tmp = boxscore_data.get(name, {})
                                for i,k in enumerate(fields):
                                    if pdata[i] == None:
                                        pdata[i] = 'None'
                                    tmp[k] = pdata[i+1].string
                                boxscore_data[name] = tmp
                            try:
                                boxscore_data[name]['team']
                            except:
                                try:
                                    boxscore_data[name]['team'] = tmp_team
                                except:
                                    continue                                
            boxscore_data['GAMETAG'] = gametag

            # meta data
            title_raw = soup.find('title').text
            meta_data['home_team'] = title_raw.split(' Box Score, ')[0].split(' at ')[1]
            meta_data['away_team'] = title_raw.split(' Box Score, ')[0].split(' at ')[0]
            meta_data['date_played'] = title_raw.split(' Box Score, ')[1].split(' |')[0]
            for row in soup.find('table',{"class" : "margin_top small_text"}):
                try:
                    if row.contents[0].text == 'Inactive:':
                        inactive_dict = {}
                        away = True
                        for i in row.contents[1].text.split('\xa0'):
                            if ':' in i:
                                if '\n' in i:
                                    away_text = i.strip('\n').strip(':')
                                    inactive_dict[away_text] = []
                                else:
                                    home_text = i.strip(':')
                                    inactive_dict[home_text] = []
                                    away = False
                            else:
                                if away is True and i not in ['']:
                                    inactive_dict[away_text].append(i.strip(','))
                                elif away is False and i not in ['']:
                                    inactive_dict[home_text].append(i.strip(','))
                        meta_data['inactive'] = inactive_dict
                    elif row.contents[0].text == 'Officials:':
                        meta_data['officials'] = []
                        for official in row.findAll('a'):
                            meta_data['officials'].append(official.text)
                    elif row.contents[0].text == 'Attendance:':
                        meta_data['attendance'] = "".join(row.text.split(':')[1].split(','))
                    elif row.contents[0].text == 'Time of Game:':
                        meta_data['time_of_game'] = row.text.split('Game:')[1]
                except:
                    continue
           
            boxscore_data.update(meta_data)

            # scoring
            scoring = {}
            for row in soup.find('table',{"class" : "nav_table stats_table"}):
                try:
                    if len(row.contents) == 13:
                        try:
                            int(row.contents[11].text)
                            scoring['{}'.format(row.contents[1].text)] = [row.contents[3].text,
                                                                          row.contents[5].text,
                                                                          row.contents[7].text,
                                                                          row.contents[9].text,
                                                                          row.contents[11].text]
                        except:
                            continue
                except:
                    continue
            boxscore_data['scoring'] = scoring

            # four-factors
            four_factors = {}
            for row in soup.findAll('table',{"id":"four_factors"}):
                try:
                    tmp_ff = row.contents[5].text.split('\n')
                    four_factors['{}'.format(tmp_ff[2])] = [tmp_ff[3],tmp_ff[4],tmp_ff[5],
                                                       tmp_ff[6],tmp_ff[7],tmp_ff[8]]
                    four_factors['{}'.format(tmp_ff[11])] = [tmp_ff[12],tmp_ff[13],tmp_ff[14],
                                                        tmp_ff[15],tmp_ff[16],tmp_ff[17]]
                except:
                    continue
            boxscore_data['four_factors'] = four_factors
            
            return boxscore_data
        else:
            print("Game {} already exists in db. Skipping web-scraping phase...".format(gametag))
            # currently returns empty dicts, but should ideally load from mongodb and return to user
            return None
            
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

    def scrape(self, year):
        """
        Public function to scrape all boxscore data for any given season from basketball-reference.com.

        Parameters
        ----------
        year : int
            The season boxscores should be scraped for. Default value is 2015

        Returns
        -------
        """
        #Get game urls
        links = self._get_game_urls_for_season(year)
      
        #Get a boxscore for each game
        for link in links:
            #Check that game isnt already in database
            if self._check_game_exists(link):
                if self.debug:
                    print("Game Already Exists: {}".format(link))
                continue #ID already exists
            bscore = self._get_boxscore(link)

            #Add each boxscore to the DB
            self._write_to_mongodb(bscore)
    
    def _check_game_exists(self, boxscore_link):
        """
        Private function that checks a link against the data we have already downloaded
        """
        # last part of the link holds the ID.
        game = boxscore_link.split('/')[-1]
        ID = game[:-5]
        
        # query the database to see if this ID already exists
        return self._ID_exists_in_DB(ID)

    def _ID_exists_in_DB(self, ID):
        """
        Private function to check if an ID exists in the database for a specific game.
        """
        assert self.client is not None, "No MongoDB Client"
        self.db = self.client.game_data
        self.posts = self.db.posts
        document = self.posts.find_one({'GAMETAG': ID})
        return document is not None
    

    def _write_to_mongodb(self, boxscore_data):
        """
        Private function which writes boxscore_data dictionary to the mongodb collection entitled, 'game_data'.

        Parameters
        ----------
        boxscore_data : dict
            The boxscore data dictionary to be written to the database.

        Returns
        -------
        """
        
        assert self.client is not None, "No MongoDB Client"
        db = self.client.game_data
        posts = db.posts
        
        post_id = posts.insert(boxscore_data)
        if self.debug is True:
            print("Added {} to database...".format(post_id))
        return post_id

    def _purge_mongodb_collection(self,collection=None):
        """
        Private function which purges a mongodb collection.

        Parameters
        ----------
        collection : str
            The name of the mongodb collection to delete.

        Returns
        -------
        """

        assert self.client is not None, "No MongoDB Client"
        db = self.client.game_data
        posts = db.posts

        assert collection is not None, "Must specify a collection name to purge from the database"
        assert collection in posts.database.name, "Collection is not in the database"
        ipdb.set_trace()
        posts.remove()
        ipdb.set_trace()
