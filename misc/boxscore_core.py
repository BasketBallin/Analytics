from bs4 import BeautifulSoup
from urllib2 import urlopen
from tabulate import tabulate
import re

class boxscore():

	def __init__(self):
		self.player_data = {}

	def get_boxscore(self, url):
		html = urlopen(url).read()
		gametag = url.split('/')[-1].strip('.html')
		soup = BeautifulSoup(html, 'lxml')
		self.search_table(soup, self.player_data, 'basic')
		self.search_table(soup, self.player_data, 'advanced')
		for player in self.player_data:
			self.player_data[player]['GAMETAG'] = gametag
		
	def search_table(self, soup, player_data, search_str):
		data_fields = {'basic':['MP','FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS','+/-'], 'advanced':['MP','TS%','eFG%','ORB%','DRB%','TRB%','AST%','STL%','BLK%','TOV%','USG%','ORtg','DRtg']}
		fields = data_fields[search_str]
	
		#Get table from html
		tables = soup.findAll('table', id=re.compile(search_str))
	
		tables = [t.find('tbody') for t in tables]
		#Get player data from basic tables
		#Instead of keeping track of all the people who played in this game
		#Lets assign a tag this game, so we can see everyone who played in a game by searching for the tag
		for t in tables:
			data = t.findAll('tr')
			for player in data:
				if player['class'][0] == '':
					pdata = player.findAll('td')
					name = pdata[0].string
					if pdata[1].string != "Did Not Play":
						tmp = player_data.get(name, {})
						for i,k in enumerate(fields):
							if pdata[i+1] == None:
								pdata[i+1] = 0
							tmp[k] = pdata[i+1].string
						self.player_data[name] = tmp

	def print_table(self):
		data = []
		for player in self.player_data:
			row = [player]
			for k in self.player_data[player]:
				row.append(self.player_data[player][k])
			data.append(row)
		print tabulate(data)





if __name__ == '__main__':
	boxscore_LAL = boxscore()
	boxscore_LAL.get_boxscore('http://www.basketball-reference.com/boxscores/201410280LAL.html')
	print boxscore_LAL.player_data

	print boxscore_LAL.player_data['Kobe Bryant']

	boxscore_LAL.print_table()


