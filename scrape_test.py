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

    def check_game_ID_exists(self):
        #Add a fake entry to the database, and check if it exists. Then delete the entry
        s2014 = Scrape(year=2014)
        db = s2014.client.game_data
        posts = db.posts

        #Add fake entry
        post = {'GAMETAG':1337, 'MP':1,'FG':1,'FGA':1,'FG%':1,'3P':1,'3PA':1,'3P%':1,
                'FT':1,'FTA':1,'FT%':1,'ORB':1,'DRB':1,'TRB':1,'AST':1,
                'STL':1,'BLK':1,'TOV':1,'PF':1,'PTS':1,'+/-':1}

        post_id = posts.insert(post)

        #Check if the GAMETAG exists
        assert s2014._ID_exists_in_DB(1337) == True

        #Remove the entry
        posts.remove({'_id':post_id})
        
        #Check if the GAMETAG is gone
        assert s2014._ID_exists_in_DB(1337) == False

    def Add_boxscore_to_mongodb(self):
        """
        Download a boxscore. Check that the ID doesnt exist. Add the boxscore to the db.
        """
        url = 'http://www.basketball-reference.com/boxscores/201502270ATL.html'
        ID = '201502270ATL'
        s2014 = Scrape(year=2014)
        boxscore_data,gametag = s2014._get_boxscore(url,field_type='basic')
        assert s2014._ID_exists_in_DB(ID) == False, "ID already exists"
        post_id = s2014._write_to_mongodb(boxscore_data)

        assert s2014.client.game_data.posts.find_one({'GAMETAG':ID}) is not None, "Data never written to db"
        s2014.client.game_data.posts.remove({'_id':post_id})



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
