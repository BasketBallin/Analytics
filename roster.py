class Roster():
    def __init__(self):
	self.Team = None
        self.Team_Short = None
	self.Players = None
        self.tmpdata = None

    def set_team(self, T, S):
        self.Team = T
        self.Team_Short = S

    def add_player(self, p):
        if self.Players is None:
            self.Players = []
        self.Players.append(p)

    def get_dict(self):
        roster_dict = {}

    def set_data(self, d):
        self.tmpdata = d

    def get_data(self):
        return self.tmpdata
