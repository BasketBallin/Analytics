from scipy import *
from matplotlib.pyplot import *
import sqlite3 as lite
from datetime import date

con = None

con = lite.connect('test.db')

#Date information
today = date.today()

with con:
	cur = con.cursor()
	cur.execute("SELECT Date, FG, ThreeP, FT, TRB, TOV FROM Data WHERE Name = \'Kobe Bryant\'")
	rows = cur.fetchall()
	stats = []
	days = []
	for row in rows:
		d = str(row[0])
		year = int(d[:4])
		month = int(d[4:6])
		day = int(d[6:])
		date_played = date(year, month, day)
		days.append( (today - date_played).days )
		stats.append(array(row[1:], dtype=float))

	print len(days)
	srt = sorted(zip(days,stats), key=lambda x: x[0])
	days, stats = zip(*srt)
	stats = array(stats)
	plot(days, stats[:,0], label='Points')	
	plot(days, stats[:,1], label='3 Pointers')	
	plot(days, stats[:,2], label='Free Throws')	
	plot(days, stats[:,3], label='Rebounds')	
	plot(days, stats[:,4], label='Turnovers')
	legend()
	xlabel('Number of days ago game was played')	
	show()
