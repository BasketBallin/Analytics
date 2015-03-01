from scrape_core import Scrape

from numpy import loadtxt
import os

# temporary imports
import json
import ipdb

# static files to test against
DATA_DIR = os.path.join(os.path.dirname(__file__), 'tests/data/')

class TestScrape(object):

    def obtain_all_2013_game_urls(self):
        # Testing the ability to obtain game urls
        s2013 = Scrape(year=2013)
        links2013 = s2013._get_game_urls_for_season()

        # load data from static text file
        urlsfromfile = loadtxt(DATA_DIR+'season2013urls.txt',
                               delimiter='\n',dtype='str')
        urlsfromfile = [i.split("'")[1] for i in urlsfromfile]
        
        assert urlsfromfile == links2013, "Links for season 2013 have not been properly downloaded..."

    def download_boxscore_and_print_to_terminal(self):
        # Get boxscore; basic then advanced
        s2013 = Scrape(year=2013)
        links2013 = s2013._get_game_urls_for_season()
        boxscore_data,gametag = s2013._get_boxscore(links2013[0],
                                                    field_type='basic')

        # load data from static json file
        f = open('./tests/data/season2013gamedata.json','r')
        gamedatafromfile = json.load(f)
        assert boxscore_data == gamedatafromfile, "Game data has not been properly downloaded..."
