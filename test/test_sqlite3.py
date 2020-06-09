import sqlite3

con = sqlite3.connect('./test.sqlite3')
# con.execute('CREATE TABLE IF NOT EXISTs mstSkill (id INTEGER PRIMARY KEY,type INTEGER,name TEXT,maxLv INTEGER,iconId INTEGER);')
# con.execute("INSERT INTO mstSkill values(1000,1,'今は脆き雪花の壁',10,400)")
con.execute('ALTER TABLE mstSkill RENAME name TO jpName')
con.commit()
con.close()
