from scraper import Scraper
from boxscore import BoxScore
from boxscore_scraper import BoxScore_Scraper

from numpy import loadtxt
import os

# temporary imports
import json
import ipdb

# static files to test against
DATA_DIR = os.path.join(os.path.dirname(__file__), 'tests/data/')

class TestBoxScore(object):

    def obtain_all_2013_game_urls(self):
        # Testing the ability to obtain game urls
        s2013 = BoxScore_Scraper(None)
        links2013 = s2013._get_game_urls_for_season(year=2013)

        # load data from static text file
        urlsfromfile = loadtxt(DATA_DIR+'season2013urls.txt',
                               delimiter='\n',dtype='str')
        urlsfromfile = [i.split("'")[1] for i in urlsfromfile]
        
        assert urlsfromfile == links2013, "Links for season 2013 have not been properly downloaded..."

    def download_boxscore_and_print_to_terminal(self):
        # Get boxscore; basic then advanced
        s2013 = BoxScore_Scraper(None)
        links2013 = s2013._get_game_urls_for_season(year=2013)
        boxscore_data = s2013._get_boxscore(links2013[0])

        # load data from static json file
        f = open('./tests/data/season2013gamedata.json','r')
        gamedatafromfile = json.load(f)
        
        assert boxscore_data == gamedatafromfile, "Game data has not been properly downloaded..."
        
    def check_game_ID_exists(self):
        #Add a fake entry to the database, and check if it exists. Then delete the entry
        scraper = Scraper()
        s2013 = BoxScore_Scraper(scraper.client)
        db = scrape.client.game_data
        posts = db.posts

        #Add fake entry
        post = {'GAMETAG':1337, 'MP':1,'FG':1,'FGA':1,'FG%':1,'3P':1,'3PA':1,'3P%':1,
                'FT':1,'FTA':1,'FT%':1,'ORB':1,'DRB':1,'TRB':1,'AST':1,
                'STL':1,'BLK':1,'TOV':1,'PF':1,'PTS':1,'+/-':1}
        post_id = posts.insert(post)

        #Check if the GAMETAG exists
        assert s2013._ID_exists_in_DB(1337) == True
        ipdb.set_trace()
        #Remove the entry
        posts.remove({'_id':post_id})
        
        #Check if the GAMETAG is gone
        assert s2013._ID_exists_in_DB(1337) == False

    def add_boxscore_to_mongodb(self):
        """
        Download a boxscore. Check that the ID doesnt exist. Add the boxscore to the db.
        """
        url = 'http://www.basketball-reference.com/boxscores/201502270ATL.html'
        ID = '201502270ATL'
        scrape = Scrape()
        s2014 = BoxScore_Scraper(scrape.client)
        boxscore_data = s2014._get_boxscore(url)
        assert s2014._ID_exists_in_DB(ID) == False, "ID already exists"
        post_id = s2014._write_to_mongodb(boxscore_data)
        ipdb.set_trace()
        assert s2014.client.game_data.posts.find_one({'GAMETAG':ID}) is not None, "Data never written to db"
        scrape.client.game_data.posts.remove({'_id':post_id})

#class TestRoster(object):
#
#    def 
