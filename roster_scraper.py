from bs4 import BeautifulSoup
from tabulate import tabulate
from urllib.request import urlopen
import re

# temporary imports
import json
import ipdb

from roster import *

class Roster_Scraper(object):

    def __init__(self):
        pass

    def _get_team_links(self):
        """
        We could either hardcode these links or scrape them.
        Might make sense to scrape them just to make sure
        incase anything changes.
        """
        url = 'http://espn.go.com/nba/players'
        link_base = 'http://espn.go.com/nba/team/roster/_/name/'
        # Begin parsing
        html = urlopen(url).read()        
        soup = BeautifulSoup(html, 'html.parser')
        ptable = soup.find('div', id='my-players-table')

        #Get small-logos tables
        small_logos = [sl for sl in ptable.findAll('ul', 'small-logos')]

        teams_links = []
        #For each small logos, for each list element, get the link to the team
        for group in small_logos:
            for team in group.findAll('li'):
                tmp = team.a['href']
                tmp = tmp.split('/')
                teams_links.append(link_base+tmp[-2]+"/"+tmp[-1])

        return teams_links
   
    def _parse_links(self, team_links):
        """
        Given a set of teawm links, get the short hand for the team, and the team name
        """
        teams = []
        for team_l in team_links:
            team = team_l.split('/')
            team_dict = {'SHORT': team[-2].upper()}
            fullname = team[-1].upper().replace('-',' ')
            team_dict['FULL'] = fullname
            team_dict['LINK'] = team_l
            teams.append(team_dict)
        return teams

    def _parse_team(self, link):
        """
        Given a link to a teams roster, get all the players and stats
        """
        html = urlopen(link).read()        
        soup = BeautifulSoup(html, 'html.parser')
        ptable = soup.find('div', id='my-players-table')
        
        rtable = ptable.find('table', 'tablehead')
        #Get each row, but only rows that have the word 'player' in them
        player_rows = [row for row in rtable.findAll('tr', re.compile('player'))]

        #Get player stats for each row
        player_dict = dict()
        for player in player_rows:
            pdict = {}
            pdata = player.findAll('td')
            pdict['NO'] = int(pdata[0].string)
            NAME = pdata[1].string
            pdict['POS'] = pdata[2].string
            pdict['AGE'] = int(pdata[3].string)
            HT = pdata[4].string.split('-')
            pdict['HT'] = float(HT[0]) + float(HT[1])/12. 
            pdict['WT'] = int(pdata[5].string)
            pdict['COLLEGE'] = pdata[6].string
            pdict['SALARY'] = int(pdata[7].string.replace('$','').replace(',',''))
            player_dict[NAME] = pdict
        return player_dict
           

    def Scrape(self):
        """
        Get links for every team. Get Team names. For each team, build the roster.
        """
        team_data = []
        links = self._get_team_links()
        ipdb.set_trace()
        teams = self._parse_links(links)
        ipdb.set_trace()
        for team in teams:
            print(team)
            tmp = self._parse_team(team['LINK'])
            #tmp['FULL'] = team['FULL']
            #tmp['SHORT'] = team['SHORT']
            #team_data[ team['SHORT'] ] = tmp
            T = Roster()
            T.set_data([team, tmp])
            team_data.append(T)
        ipdb.set_trace()


