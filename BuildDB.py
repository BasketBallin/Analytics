from roster_core import *
from season_core import *
from boxscore_core import *
import json

#Get links to all games for the season
season_2015 = Season(year=2014)

#Get data for each game
for tmp_game in season_2015.game_links:

	print tmp_game

	#Download Boxscore
	bscore = boxscore()
	bscore.get_boxscore(tmp_game)
	bscore.print_table()
	keys = bscore.player_data.keys()
	gametag = bscore.player_data[keys[0]]['GAMETAG']
	
	with open('../'+gametag+'.json','w') as f:
		json.dump(bscore.player_data, f)
