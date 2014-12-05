from bs4 import BeautifulSoup
#from urllib2 import urlopen
import urllib2
import zlib
import re

class Season():

	def __init__(self, year=None):
		self.year = year
        	assert self.year is not None, "Must specify an Season."
		self.base = 'http://www.basketball-reference.com'
		self.game_url = self.base+"/leagues/NBA_"+str(year)+"_games.html"
		self.game_links = self._get_games_for_season()
		
	def _get_games_for_season(self):
		html = urllib2.urlopen(self.game_url).read()
		#request = urllib2.Request(self.game_url)
		#request.add_header('Accept-Encoding', 'gzip')
		#response = urllib2.urlopen(request)
		#html = zlib.decompress(response.read(), 16 + zlib.MAX_WBITS)
		#html = ''
		#fp = urllib2.urlopen(self.game_url)
		#while 1:
		#	data = fp.read()
		#	if not data:
		#		break
		#	html += data
		soup = BeautifulSoup(html, 'html.parser')
		table = soup.find('table', 'sortable stats_table')
		
		#Get each row of the table
		table = table.find('tbody')
		rows = [row for row in table.findAll('tr')]
	
		#Get the box score link for each row
		boxscore_links = [self.base+row.findAll('td')[1].a['href'] for row in rows if row.findAll('td')[1].string == 'Box Score']
	
		return boxscore_links

if __name__ == '__main__':
	season_2014 = Season(year=2014)
	print season_2014.game_links
