from bs4 import BeautifulSoup
import urllib2
# Imports needed to open the DB and interact with it:
from ZODB import DB
from ZODB.FileStorage import FileStorage
from ZODB.PersistentMapping import PersistentMapping
import transaction
from persistent import Persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList
import time
import ipdb

def open_db(path):
    zdb = {}
    zdb['storage'] = FileStorage(path + 'NBA_Roster_ZODB.fs')
    zdb['db'] = DB(zdb['storage'])
    zdb['connection'] = zdb['db'].open()
    zdb['root'] = zdb['connection'].root()
    return zdb

def close_db(zdb):
    transaction.get().abort()
    zdb['connection'].close()
    zdb['db'].close()
    zdb['storage'].close()


class Roster():
    
    def __init__(self,team=None,path=None):
        self.team = team
        assert self.team is not None, "Must specify an organization."
        self.default_path = '/Users/groenera/Desktop/'
        if path is None:
            self.path = self.default_path
        else:
            self.path = path
        
    def _build_team_database_dict(self,skip=False):
        url_teams = "http://espn.go.com/nba/teams"
        response = urllib2.urlopen(url_teams)
        html = response.read()
        soup = BeautifulSoup(html)
        links_raw = [i.get('href') for i in soup.find_all('a')]
        tmp =  [i for i in links_raw if type(i) == str]
        teams_raw = [i for i in tmp if 'team/_/name' in i]
        teams = [i.split('/')[-1].split('-') for i in teams_raw]
        self.team_dict = {}
        exceptions = ['portland']
        for i in teams:
            if len(i) == 2:
                self.team_dict['{}'.format(i[0])]=i[1]
            if len(i) == 3:
                if i[0] in exceptions:
                    self.team_dict['{}'.format(i[0])] = str(i[1]) + " " + str(i[2])
                else:
                    self.team_dict['{} {}'.format(i[0],i[1])] = i[2]
        self.team_rosterurl_dict = {}
        for i in self.team_dict.keys():
            for j in teams_raw:
                if len(i.split(' ')) > 1:
                    if i.split(' ')[0] in j:
                        self.team_rosterurl_dict['{}'.format(i)]=j
                else:
                    if i in j:
                        self.team_rosterurl_dict['{}'.format(i)]=j
        self.team_roster_dict = {}
        if skip is False:
            for i in self.team_dict.keys():
                url = self.team_rosterurl_dict[i].split('_')[0]+"roster/_"+self.team_rosterurl_dict[i].split('_')[1]
                response = urllib2.urlopen(url)
                html = response.read()
                soup = BeautifulSoup(html)
                tables = soup('table')
                self.team_roster_dict['{}'.format(i)] = {}
                for table in tables:
                    rows = table('tr')
                    for row in rows:
                        data = row('td')
                        try:
                            int(data[0].renderContents())
                            name = data[1].renderContents().split('>')[1].split('<')[0]
                            self.team_roster_dict[i][name] = {}
                            self.team_roster_dict[i][name]['NO'] = int(data[0].renderContents())
                            self.team_roster_dict[i][name]['POS'] = data[2].renderContents()
                            self.team_roster_dict[i][name]['AGE'] = int(data[3].renderContents())
                            self.team_roster_dict[i][name]['HT'] = data[4].renderContents()
                            self.team_roster_dict[i][name]['WT'] = int(data[5].renderContents())
                            self.team_roster_dict[i][name]['COLLEGE'] = data[6].renderContents()
                            self.team_roster_dict[i][name]['2014-2015 SALARY'] = data[7].renderContents()
                        except ValueError:
                            continue
                    
    def _build_team_database(self,path=None):
        if path is None:
            path = self.path
        zdb = open_db(path)
        
        # check to see if db has 29 teams
        db_check=self._check_team_database(zdb,warn=False)
        # if database exists, rebuild self.team_dict
        if db_check is 1:
            ipdb.set_trace()
            return

        t = time.localtime()

        # check to see if self.team_roster_dict exists
        try:
            self.team_dict
            self.team_roster_dict
        except AttributeError:
            self._build_team_database_dict()

        try:
            zdb['root']['team']
        except KeyError:
            zdb['root']['team'] = PersistentDict()
            
        for team in self.team_roster_dict.keys():
            # Checking to see if team data has already been added for this database
            try:
                zdb['root']['team']['{}'.format(team)]
            except KeyError:
                zdb['root']['team'][team] = PersistentDict()
                for player in self.team_roster_dict[team].keys():
                    zdb['root']['team'][team][player] = PersistentDict()
                    for stat in self.team_roster_dict[team][player].keys():
                        zdb['root']['team'][team][player][stat] = PersistentDict()
                        zdb['root']['team'][team][player][stat] = self.team_roster_dict[team][player][stat]
                zdb['root']['team'][team]['date_added'] = "Date:{}/{}/{}, Time:{}h{}m{}s".format(t.tm_mon,t.tm_mday,t.tm_year,t.tm_hour,t.tm_min,t.tm_sec)
            else:
                print("Warning: Attempting to overwrite a team: {}.".format(team))
    
        transaction.get().commit()

        close_db(zdb)

    def _check_team_database(self,zdb,warn=False):
        if warn is True:
            assert len(zdb['root'].keys()) > 0, "Warning: The database appears to be empty.." 
            assert len(zdb['root']['team'].keys())==29, "Warning: The database appears to be incomplete.."
        else:
            if len(zdb['root'].keys()) > 0:
                if len(zdb['root']['team'].keys())!=29:
                    return 0
                else:
                    return 1
            else:
                return 2

    def _check_db_exists(self,path=None):
        if path is None:
            path = self.path
        zdb = open_db(path)
        try:
            zdb['root']['team'].keys()
            close_db(zdb)
            return 1
        except KeyError:
            close_db(zdb)
            return 0
        
    def get_roster(self,path=None):
        if path is None:
            path = self.path
        
        db_exists = self._check_db_exists()
        if db_exists is 1:
            self._build_team_database_dict(skip=True)
            team = [i for i in self.team_dict.keys() if self.team_dict[i] == self.team.lower()][0]
            zdb = open_db(path)
            tmp = zdb['root']['team']['{}'.format(team)]
            tmp_team_dict = {}
            for player in tmp.keys():
                tmp_team_dict[player] = {}
                if player not in ['date_added']:
                    for attr in tmp[player].keys():
                        tmp_team_dict[player][attr] = tmp[player][attr]
                else:
                    tmp_team_dict[player] = tmp[player]
            close_db(zdb)
            return tmp_team_dict
        else:
            print("Building team roster database for the first time..")
            self._build_team_database(path=self.path)
            team = [i for i in self.team_dict.keys() if self.team_dict[i] == self.team.lower()][0]
            return self.team_roster_dict[team]


if __name__ == '__main__':
    celtics = Roster(team='Celtics')
    celtics_roster = celtics.get_roster()
