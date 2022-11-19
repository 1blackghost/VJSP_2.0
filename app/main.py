from flask import *
import re
import ast
import random
import hashlib
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3
from datetime import datetime
import pytz

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
UTC = pytz.utc
  

IST = pytz.timezone('Asia/Kolkata')
  

app=Flask(__name__)
app.secret_key="blahblah"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #16MB

#globals
term=""

@app.route("/old/getFromDB/<name>")
def getOld(name):
	if "user" in session:
		import sqlite3
		conn=sqlite3.connect("prime.db")
		c=conn.cursor()
		c.execute("""SELECT * FROM prime""")
		msg=c.fetchall()
		if str(name)=="ALL":

			return render_template("oldmsg.html",msg=msg,me=session["user"])
		else:
			string=""
			lock=False
			newArr=[]
			for i in msg:
				if i[3]=="bluekeySecrect":
					string=i[0]+":"+i[1]+":"+i[2]
					if (name==string):
						lock=True
					else:
						lock=False
				if lock:
					newArr.append(i)
			return render_template("oldmsg.html",msg=msg,me=session["user"])





	else:
		return redirect(url_for("dashboard"))




@app.route("/getLike/<L_id>",methods=["POST","GET"])
def liker(L_id):
	with open("likes.ash","r") as f:
		data=eval(f.read())
	flag=False
	oops=True
	y=0
	move=True
	try:
		temp2=[]
		getVal=[]
		for i in data:
			if int(i[0])==int(L_id):
				if str(session["user"]) in i:
					oops=False
					y=i[1]
					y=y-1
					i[1]=y
					i.remove(str(session["user"]))
					con=sqlite3.connect("messages.db")
					c=con.cursor()
					c.execute(f'UPDATE messages SET likes = (?) WHERE m_id=(?);',(str(y),str(L_id)))
					con.commit()
					temp2.append(i)
					
			else:
				temp2.append(i)
		if not oops:
			with open("likes.ash","w") as f:
				f.write(str(temp2))

			return ('', 204)
		temp=[]
		for i in data:
			if ((i[0]==L_id) and (oops)):
				o=i[1]
				o=o+1
				i[1]=o
				con=sqlite3.connect("messages.db")
				c=con.cursor()
				c.execute(f'UPDATE messages SET likes = (?) WHERE m_id=(?);',(str(o),str(L_id)))
				con.commit()
				i.append(str(session["user"]))
				flag=True
			else:
				temp.append(i)

		l=[]
		if not flag:
			l.append(L_id)
			l.append(1)
			l.append(session["user"])
			data.append(l)
		with open("likes.ash","w") as f:
			f.write(str(data))
		return ('', 204)
	except Exception as e:
		print(e)
		return "Error Unknown Contact VJSP Admin with code :#1048"

def create_new_message_id():
	with open("message_current_id.txt","r") as f:
		data=int(f.read())
	data=data+1
	with open("message_current_id.txt","w") as f:
		f.write(str(data))
	return str(data)

@app.route("/trash/<name>",methods=["POST","GET"])
def deletion_trash(name):
	con=sqlite3.connect("messages.db")
	c=con.cursor()
	c.execute("""SELECT * FROM messages""")
	msg=c.fetchall()
	for i in msg:
		if ((i[2]==name) and (i[0]==session["user"])):
			sql = "DELETE FROM messages WHERE m_id ="+str(name)

			c.execute(sql)

			con.commit()
			return ('', 204)
	else:
		return "Unauthorised Access! Enna Mwonu Hack Panna Pakala? Err-401"

@app.route('/success', methods = ['POST'])
def success():
	if 'user' in session:
		if request.method == 'POST':
			f = request.files['file']
			to='static/'+str(f.filename)
			print(f.filename)
			datetime_ist = datetime.now(IST)
			current= datetime_ist.strftime('%H:%M:%S %Z')
			if ((str(f.filename).endswith("png")) or (str(f.filename).endswith("jpg")) or (str(f.filename).endswith("jpeg"))):
				f.save(to)
				name=f.filename
				user=session["user"]
				con=sqlite3.connect("messages.db")
				c=con.cursor()
				url="http://127.0.0.1:5000"
				message=str("detectionIMage~")+str(url)+url_for('static', filename=name)
				message=str(message)
				m_id=create_new_message_id()
				c.execute(f'INSERT INTO messages VALUES (?,?,?,?,?)',(user,message,m_id,'0',str(current)))
				con.commit()
				return redirect(url_for('dashboard'))
			if ((str(f.filename).endswith("gif")) or (str(f.filename).endswith("mp4")) or (str(f.filename).endswith("avi")) or (str(f.filename).endswith("mkv")) or (str(f.filename).endswith("webm")) or (str(f.filename).endswith("3gp")) ):    
				f.save(to)
				name=f.filename
				user=session["user"]
				con=sqlite3.connect("messages.db")
				c=con.cursor()
				url="http://127.0.0.1:5000"
				message=str("detectionVideo~")+str(url)+url_for('static', filename=name)
				message=str(message)
				m_id=create_new_message_id()
				c.execute(f'INSERT INTO messages VALUES (?,?,?,?,?)',(user,message,m_id,'0',str(current)))
				con.commit()
				return redirect(url_for('dashboard'))
			else:
	
				user=session["user"]
				con=sqlite3.connect("messages.db")
				c=con.cursor()
				message=str(user)+" have tried to upload a file of suspicious and unacceptable formats!"
				message=str(message)
				m_id=create_new_message_id()
				c.execute(f'INSERT INTO messages VALUES (?,?,?,?,?)',(user,message,m_id,'0',str(current)))
				con.commit()
				return redirect(url_for('dashboard'))
@app.route("/sendFile")
def send_file():
	return render_template("upload_file.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('not_found.html'), 404

@app.route("/donate")
def donate():
	return render_template("donate.html")
@app.route("/update_user_here",methods=["POST"])
def update_users():
    file = open('update_user.ash', encoding="utf8")
    mess=eval(file.read())
    return jsonify('',render_template('update_user_here.html',users=mess))



@app.route("/getM",methods=["GET","POST"])
def getM():
	if "user" in session:
		message=request.form["text"]

		message=str(message)
		user=session["user"]
		con=sqlite3.connect("messages.db")
		c=con.cursor()
		m_id=create_new_message_id()
		datetime_ist = datetime.now(IST)
		current= datetime_ist.strftime('%H:%M:%S %Z')
		c.execute(f'INSERT INTO messages VALUES (?,?,?,?,?)',(user,message,m_id,'0',str(current)))
		con.commit()
		with open("likes.ash","r") as f:
			data=eval(f.read())
		l=[]
		l.append(m_id)
		l.append(0)
		data.append(l)
		with open("likes.ash","w") as f:
			f.write(str(data))
		return json.dumps({'status':'OK'})
	else:
		return redirect(url_for("dashboard"))



@app.route("/update",methods=["POST"])
def update():
	con=sqlite3.connect("messages.db")

	c=con.cursor()
	c.execute("""SELECT * FROM messages""")
	messages=c.fetchall()
	return jsonify('',render_template('update.html',msg=messages,me=str(session['user'])))
def send_reset_link(r_email,url):


	password = "vprdretileiglktv"

	port = 465  
	smtp_server = "smtp.gmail.com"
	sender_email = "vjspmain@gmail.com" 
	receiver_email = r_email
	msg = MIMEMultipart('alternative')
	msg['To'] = receiver_email
	msg['From'] = sender_email
	msg['Subject'] = 'USER CREDENTIALS CHANGE REQUEST-VJSP'

	text = '''<h1>USER CREDENTIALS CHANGE REQUEST-VJSP</h1>
	<p>

	Hi There, The Request for password/user credentials change has been processed ,please use the link below
	<br>CLICK HERE TO CONTINUE:
	    <br>
	        <br>
	            <br>
	  <a style="background-color: green; padding: 10px 20px;
	            color: white; text-decoration:none;font-size:14px;
	            font-family:Roboto,sans-serif;border-radius:5px" href="{}">Change Password/User Details
	  </a>
	  <p style="color:blue;">This is one-time-only link! Use wisely</p>

	  <p style="color:red;">This is a system generated message do not reply!</p>
	</p>'''.format(url)

	part2 = MIMEText(text, 'html')

	msg.attach(part2)

	s = smtplib.SMTP(smtp_server,587)
	s.ehlo()
	s.starttls()
	s.login(sender_email,password)
	s.sendmail(sender_email, receiver_email, msg.as_string())
	s.quit()


@app.route("/forgot_password/reset/<name>",methods=["GET","POST"])	
def forgot_password_reset(name):
	if request.method=="POST":
		name=request.form["name"]
		password=request.form["pass"]
		re_password=request.form["re_pass"]
		email=session["changee"]
		data_acc=[]
		with open("db.ash","r") as f:
			data=eval(f.read())
		for i in data:
			if name=="" or password=="" or re_password=="":
				msg="Blank Fields Detected!"
				return render_template("change_passworderror.html",msg=msg,name=name,password=password,email=email)
			if password!=re_password:
				msg="Passwords Doesn't Match!"
				return render_template("change_passworderror.html",msg=msg,name=name,password=password,email=email)
			if len(password)<6:
				msg="Provide A Password with 6 charcters or higher!"
				return render_template("change_passworderror.html",msg=msg,name=name,password=password,email=email)
		with open("db.ash","r") as f:
			data=eval(f.read())
		for i in data:
			if i[1]==email:
				if i[0]==name and i[2]==password and i[1]==email:
					msg="No Credentials Have Been Changed!"
					dum=[]
					with open("fbuffer.ash","r") as f:
						cred=eval(f.read())
					for i in cred:
						if i[1]==email:
							pass
						else:
							dum.append(i)
							
					with open("fbuffer.ash","w") as f:
						f.write(str(dum))
					return render_template("message_only.html",msg=msg)
				i[0]=name
				i[2]=password

		with open("db.ash","w") as f:
			f.write(str(data))
		msg="Credentials Changed!"
		dum=[]
		with open("fbuffer.ash","r") as f:
			cred=eval(f.read())
		for i in cred:
			if i[1]==email:
				pass
			else:
				dum.append(i)
							
		with open("fbuffer.ash","w") as f:
			f.write(str(dum))
		return render_template("message_only.html",msg=msg)


	with open("fbuffer.ash","r") as f:
		data=eval(f.read())
	for i in data:
		if (name==i[3]):
			email=i[1]
			name=i[0]
			password=i[2]
			if "changee" in session:
				session.pop("changee")
				
			session["changee"]=email
			return render_template("change_password.html",email=email,password=password,name=name)
	return redirect(url_for("signin"))

@app.route("/forgot_password",methods=["GET","POST"])
def forgot_password():
	if request.method=="POST":
		femail=request.form["your_name"]
		print(femail)
		checker_list=[]
		data_acc=[]
		with open("db.ash","r") as f:
			data=eval(f.read())
		for i in data:
			if (femail==i[0]) or (femail==i[1]):
				email=i[1]
				name=i[0]
				password=i[2]

				with open("fbuffer.ash","r") as f:
					buffer_data=eval(f.read())
				if len(buffer_data)<5:

					for i in buffer_data:
						if email==i[1]:
							pass
						else:
							checker_list.append(i)
				data_acc.append(name)
				data_acc.append(email)
				data_acc.append(password)
				uuid=createuuid(name,email,password)
				data_acc.append(uuid)
				checker_list.append(data_acc)

				with open("fbuffer.ash","w") as f:
					f.write(str(checker_list))
				url_send=" https://3a89-2409-4073-4e1a-dd44-a5d7-9cb5-dbea-e60a.in.ngrok.io/forgot_password/reset/"+str(uuid)
				send_reset_link(email,url_send)
				msg="Email Has Been Sent To reset your password/User Details"
				return render_template("message_email.html",msg=msg)
		msg="Error: Email Or Name Verification Failed/User Doesn't Exists Yet."
		return render_template("signuperror.html",msg=msg)
	return render_template("forgot.html")

@app.route("/logout")
def logout():
	if "user" in session:

		with open("update_user.ash","r") as f:
			users=eval(f.read())
		newlist=[]
		for i in users:
			if str(i)==str(session["user"]):
				pass
			else:
				newlist.append(i)
		with open("update_user.ash","w") as f:
			f.write(str(newlist))
		session.pop("user")
		return redirect(url_for("signin"))

	else:
		return redirect(url_for("signin"))


@app.route("/user/dashboard",methods=["POST","GET"])
def dashboard():

	if "user" in session:
		con=sqlite3.connect("messages.db")
		c=con.cursor()
		c.execute("""SELECT * FROM messages""")
		msg=c.fetchall()
		with open("update_user.ash") as f:
			users=eval(f.read())
		conn=sqlite3.connect("prime.db")
		c=conn.cursor()

		c.execute("""SELECT * FROM prime""")
		old=c.fetchall()
		newArr=["ALL"]
		string=""
		for i in old:
			if i[3]=="bluekeySecrect":
				string=i[0]+":"+i[1]+":"+i[2]
				newArr.append(string)

		return render_template("index.html",msg=msg,users=users,me=session["user"],old=newArr)
	else:
		return redirect(url_for("signin"))

@app.route("/email_verification/<name>")
def verification_process(name):
	found=False
	try:
			checker_list=[]
			with open("buffer.ash","r") as f:
				buffer_data=eval(f.read())
			newl=[]
			checking=[]
			for i in buffer_data:
				if name==i[3]:
					newl.append(i[0])
					newl.append(i[1])
					newl.append(i[2])
					with open("db.ash","r") as f:
						data=eval(f.read())
					data.append(newl)
					with open("db.ash","w") as f:
						f.write(str(data))
					found=True
				else:
					checking.append(i)
			if found:
				with open("buffer.ash","w") as f:
					f.write(str(checking))
				msg="Email Successfully Verified! Redirecting Shortly..."
				return render_template("message_only.html",msg=msg,value=1)
			else:
				return redirect(url_for("signin"))

	except:
		return redirect(url_for("signin"))

def send_email_verification(r_email,url):


	password = "vprdretileiglktv"

	port = 465  
	smtp_server = "smtp.gmail.com"
	sender_email = "vjspmain@gmail.com" 
	receiver_email = r_email
	msg = MIMEMultipart('alternative')
	msg['To'] = receiver_email
	msg['From'] = sender_email
	msg['Subject'] = 'EMAIL VERIFICATION-VJSP'

	text = '''<h1>EMAIL VERIFICATION FOR-VJSP</h1>
	<p>
	    Hi there, welcome the vimal jyothi students portal,
	    Its time for you to take part in the wonderful journey with the help of your fellow students and friends
	    You are now one step ahead from becoming the part of the community
	    VERIFY AND JOIN NOW:
	    <br>
	        <br>
	            <br>
	  <a style="background-color: green; padding: 10px 20px;
	            color: white; text-decoration:none;font-size:14px;
	            font-family:Roboto,sans-serif;border-radius:5px" href="{}">Verify Now
	  </a>

	  <p style="color:red;">This is a system generated message do not reply!</p>
	</p>'''.format(url)

	part2 = MIMEText(text, 'html')

	msg.attach(part2)

	s = smtplib.SMTP(smtp_server,587)
	s.ehlo()
	s.starttls()
	s.login(sender_email,password)
	s.sendmail(sender_email, receiver_email, msg.as_string())
	s.quit()

def createuuid(name,email,password):
	def create_random_string():
		string=""
		for i in range(1,10):
			r=random.randint(1,3445)
			string=string+str(r)
		return string

	string=create_random_string()
	result=str(name)+str(email)+str(password)+str(string)
	result = hashlib.md5(result.encode())

	return result.hexdigest()

def check(email):
	if (re.fullmatch(regex, email)):
		return True
	else:
		return False

@app.route("/",methods=["GET","POST"])
def signin():
	if request.method=="POST":
		name=request.form["your_name"]
		password=request.form["your_pass"]
		with open("db.ash","r") as f:
			data=eval(f.read())	
		authen=False
		for i in data:
			if (name==i[0]) or (name==i[1]):
				if (password==i[2]):
					session['user']=i[0]
					authen=True
		if authen:
			with open("update_user.ash","r") as f:
				data=eval(f.read())
			checks=False
			for i in data:
				if str(session["user"])==str(i):
					checks=True

			if not checks:
				data.append(str(session["user"]))
				with open("update_user.ash","w") as f:
					f.write(str(data))




			return redirect(url_for("dashboard"))
		msg="Inavid Email/Password Or User Doesn't Exists!"
		return render_template("signinerror.html",msg=msg)


	return render_template("signin.html")
@app.route("/signup",methods=["GET","POST"])
def signup():
	if request.method=="POST":
		name=request.form["name"]
		email=request.form["email"]
		password=request.form["pass"]
		re_password=request.form["re_pass"]
		try:
			global term
			term=request.form["agree-term"]
		except:
			msg="You Must Agree To The Terms And Conditions"
			return render_template("signuperror.html",msg=msg)
		print(name,email,password,re_password,term)
		data_acc=[]
		with open("db.ash","r") as f:
			data=eval(f.read())
		for i in data:
			if name=="" or email=="" or password=="" or re_password=="":
				msg="Blank Fields Detected!"
				return render_template("signuperror.html",msg=msg)
			if name in i[0]:
				msg="The User-Name Already Exists Try Another One!"
				return render_template("signuperror.html",msg=msg)
			if email in i[1]:
				msg="Email Address Already Exists try logging in!"
				return render_template("signuperror.html",msg=msg)
			if not check(email):
				msg="Invalid Email Spoof Identified!"
				return render_template("signuperror.html",msg=msg)
			if password!=re_password:
				msg="Passwords Doesn't Match!"
				return render_template("signuperror.html",msg=msg)
			if len(password)<6:
				msg="Provide A Password with 6 charcters or higher!"
				return render_template("signuperror.html",msg=msg)
		checker_list=[]
		with open("buffer.ash","r") as f:
			buffer_data=eval(f.read())
		if len(buffer_data)<5:

			for i in buffer_data:
				if email==i[1]:
					pass
				else:
					checker_list.append(i)
		data_acc.append(name)
		data_acc.append(email)
		data_acc.append(password)
		uuid=createuuid(name,email,password)
		data_acc.append(uuid)
		checker_list.append(data_acc)

		with open("buffer.ash","w") as f:
			f.write(str(checker_list))
		url_send=" https://3a89-2409-4073-4e1a-dd44-a5d7-9cb5-dbea-e60a.in.ngrok.io/email_verification/"+str(uuid)
		send_email_verification(email,url_send)
		msg="Email Verification Link Has Been Sent! Verify to activate account"
		return render_template("message_email.html",msg=msg)
	return render_template("signup.html")


if __name__=="__main__":
	app.run(debug=True)