import sqlite3
import pytz
from datetime import datetime


conn=sqlite3.connect("prime.db")
conn2=sqlite3.connect("messages.db")
c=conn.cursor()
c2=conn2.cursor()
c2.execute("""SELECT * FROM messages""")
msg=c2.fetchall()
print(msg)
IST = pytz.timezone('Asia/Kolkata')
  
datetime_ist = datetime.now(IST)
current= datetime_ist.strftime('%Y:%m:%d')
current=current.split(":")
c.execute(f'INSERT INTO prime VALUES (?,?,?,?,?)',(current[0],current[1],current[2],"bluekeySecrect","aldotheapache"))

conn.commit()

for i in msg:
	c.execute(f'INSERT INTO prime VALUES (?,?,?,?,?)',(i[0],i[1],i[2],i[3],i[4]))
	conn.commit()

c2.execute(" DROP TABLE messages")
conn2.commit()
conn=sqlite3.connect("messages.db")
c=conn.cursor()

c.execute("""CREATE TABLE messages (user text,message text,m_id text,likes text,time text)""")
c.execute("""INSERT INTO messages VALUES ("SYSADMIN","The Better Day Starts Today","0","0","Now")""")
conn.commit()

