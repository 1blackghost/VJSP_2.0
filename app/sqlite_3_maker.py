import sqlite3
conn=sqlite3.connect("messages.db")
c=conn.cursor()

c.execute("""CREATE TABLE messages (user text,message text,m_id text,likes text,time text)""")
c.execute("""INSERT INTO messages VALUES ("ashish","me","0","0","Now")""")
conn.commit()

'''

c.execute("""SELECT * FROM prime""")
msg=c.fetchall()
print(msg)
'''
