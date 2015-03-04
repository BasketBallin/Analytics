from pymongo import MongoClient

# temporary or testing imports
import os.path #Can be removed once we set up the db
#import ipdb

class Scrape(object):

    def __init__(self,debug=False):
        self.debug=debug
        try:
            self.client = MongoClient()
        except:
            print("MongoDB: Connection refused")
        
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
        Private Function to check if an ID exists in the database for a specific game.
        """
        self.db = self.client.game_data
        self.posts = self.db.posts
        document = self.posts.find_one({'GAMETAG': ID})
        return document is not None
    

    def _write_to_mongodb(self, boxscore_data):
        db = self.client.game_data
        posts = db.posts
        
        post_id = posts.insert(boxscore_data)
        return post_id
    
