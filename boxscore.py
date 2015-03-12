class BoxScore(object):
    def __init__(self):
        self.boxscore_data = None
        pass

    def set_data(self, data):
        self.boxscore_data = data

    def get_data(self):
        return self.boxscore_data
