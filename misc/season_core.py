from bs4 import BeautifulSoup
from urllib2 import urlopen
import re

class Season():

	def __init__(self, year=None):
		self.year = year
        	assert self.year is not None, "Must specify an Season."
		self.base = 'http://www.basketball-reference.com'
		self.game_url = self.base+"/leagues/NBA_"+str(year)+"_games.html"
		self.game_links = self._get_games_for_season()
		
	def _get_games_for_season(self):
		html = urlopen(self.game_url).read()
		soup = BeautifulSoup(html, 'lxml')
		table = soup.find('table', 'sortable stats_table')
		
		#Get each row of the table
		table = table.find('tbody')
		rows = [row for row in table.findAll('tr')]
	
		#Get the box score link for each row
		boxscore_links = [self.base+row.findAll('td')[1].a['href'] for row in rows]
	
		return boxscore_links

if __name__ == '__main__':
	season_2014 = Season(year=2014)
	print season_2014.game_links
