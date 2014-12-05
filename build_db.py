import sqlite3 as lite
import sys
import json

con = None

con = lite.connect('test.db')

with con:
	cur = con.cursor()
	cur.execute("DROP TABLE IF EXISTS Data")
	cur.execute("CREATE TABLE Data(Id INT, Name TEXT, Date DATE, STLPercent TEXT, FT TEXT, GAMETAG TEXT, ThreeP TEXT, TOV TEXT, FG TEXT, ThreePA TEXT, DRB TEXT, ORBPercent TEXT, BLKPercent TEXT, AST TEXT, PF TEXT, FTPercent TEXT, PTS TEXT, FGA TEXT, STL TEXT, TRB TEXT, TOVPercent TEXT, ASTPercent TEXT, FTA TEXT, eFGPercent TEXT, BLK TEXT, FGPercent TEXT, PlusMinus TEXT, USGPercent TEXT, DRBPercent TEXT, TSPercent TEXT, MP TEXT, DRtg TEXT, ORtg TEXT, TRBPercent TEXT, ORB TEXT, ThreePPercent TEXT);")
	flist = open(sys.argv[1]).readlines()
	for f in flist:
		with open(f.strip()) as game_file:
			print f.strip()
			data = json.load(game_file)
			for player in data:
				tmp_fields = data[player].keys()
				fields = ['Name', 'Date']
				for i in tmp_fields:
					fields.append(i.replace('%', 'Percent').replace('+','Plus').replace('-','Minus').replace('/','').replace('3','Three'))
				vals = data[player].values()
				vals.insert(0, player)
				vals.insert(1, data[player]['GAMETAG'][:-4])
				placeholder = "?"
				fieldlist = ",".join(fields)
				placeholderlist = ",".join([placeholder]*len(fields))
				query = "INSERT INTO Data (%s) VALUES (%s);" % (fieldlist, placeholderlist)
				cur.execute(query, vals)

	#Now try getting some data
	cur.execute("SELECT Date, ThreeP FROM Data WHERE Name = \'Kobe Bryant\'")
	rows = cur.fetchall()
	for row in rows:
		print row	

	
				

