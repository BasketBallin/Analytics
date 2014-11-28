from bs4 import BeautifulSoup
import urllib2

class Roster():
    
    def __init__(self,team=None):
        self.team = team
        assert self.team is not None, "Must specify an organization."
        
    def _build_team_database(self):
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
                    
    def get_roster(self):
        try:
            self.team_roster_dict
            team = [i for i in self.team_dict.keys() if self.team_dict[i] == self.team.lower()][0]
            return self.team_roster_dict[team]
        except AttributeError:
            print("Building team roster database for the first time..")
            self._build_team_database()
            team = [i for i in self.team_dict.keys() if self.team_dict[i] == self.team.lower()][0]
            return self.team_roster_dict[team]

if __name__ == '__main__':
    celtics = Roster(team='Celtics')
    celtics_roster = celtics.get_roster()
