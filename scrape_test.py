from scrape_core import Scrape

from numpy import loadtxt
import os

# temporary imports
import ipdb

# static files to test against
DATA_DIR = os.path.join(os.path.dirname(__file__), 'tests/data/')

class TestScrape(object):

    def obtain_all_2014_game_urls(self):
        # Testing the ability to obtain game urls
        s2014 = Scrape(year=2014)
        links2014 = s2014._get_game_urls_for_season()

        # load data from static file
        urlsfromfile = loadtxt(DATA_DIR+'season2014urls.txt',
                               delimiter='\n',dtype='str')
        urlsfromfile = [i.split('"')[1] for i in urlsfromfile]
        
        assert urlsfromfile == links2014, "Links for season 2014 have not been properly downloaded"

    def download_boxscore_and_print_to_terminal(self):
        # Get boxscore; basic then advanced
        links2014 = s2014._get_game_urls_for_season()
        boxscore_data,gametag = s2014._get_boxscore(links2014[0],field_type='basic')

        s2014.display_boxscore(boxscore_data)
        #s2014._dump_gamedata_to_json(boxscore_data,gametag)

    # Test #2: Store game data for all basketball games
    # for 2013 season. Check to see if any have been
    # dumped to json files previously. Eventually, check
    # against database rather than json file.
    s2013 = Scrape(year=2013,debug=True)
    '''
    links2013 = s2013._get_game_urls_for_season()
    for li in links2013:
        boxscore_data,gametag = s2013._get_boxscore(li,field_type='advanced')
        s2013._dump_gamedata_to_json(boxscore_data,gametag)
        boxscore_data,gametag = s2013._get_boxscore(li,field_type='basic')
        s2013._dump_gamedata_to_json(boxscore_data,gametag)
    '''
