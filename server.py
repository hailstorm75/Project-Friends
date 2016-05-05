import os
import time
import sqlite3
from bottle import app, error, get, post, route, redirect, request, run, static_file, template, url
lan = "cz"
if lan == "en":
	from en import *
elif lan == "cz":
	from cz import *
elif lan == "ru":
	from ru import *

app = app()

# Creating/connecting to database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Creating/connecting to tableles
c.execute('CREATE TABLE IF NOT EXISTS friends(user_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, met_how INTEGER, met_when TEXT, bday TEXT, zodiac TEXT, gender TEXT, desc TEXT,UNIQUE(user_id, name))')
c.execute('CREATE TABLE IF NOT EXISTS metHow(how_id INTEGER PRIMARY KEY AUTOINCREMENT, how TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS diary(article_id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, article TEXT, date TEXT)')

## General functions
# Get zodiac name
def getZodiac(value):
	if value != None:
		zodiac_sign = ""
		dates = value.split(".")
		if checkInt(dates[0]) == True and checkInt(dates[0]) == True:
			if ((int(dates[1])==12 and int(dates[0]) >= 22) or (int(dates[1])==1 and int(dates[0]) <= 19)): zodiac_sign = "Capricorn"
			elif ((int(dates[1])==1 and int(dates[0]) >= 20) or (int(dates[1])==2 and int(dates[0]) <= 18)): zodiac_sign = "Aquarius"
			elif ((int(dates[1])==2 and int(dates[0]) >= 19) or (int(dates[1])==3 and int(dates[0]) <= 20)): zodiac_sign = "Pisces"
			elif ((int(dates[1])==3 and int(dates[0]) >= 21) or (int(dates[1])==4 and int(dates[0]) <= 19)): zodiac_sign = "Aries"
			elif ((int(dates[1])==4 and int(dates[0]) >= 20) or (int(dates[1])==5 and int(dates[0]) <= 20)): zodiac_sign = "Taurus"
			elif ((int(dates[1])==5 and int(dates[0]) >= 21) or (int(dates[1])==6 and int(dates[0]) <= 20)): zodiac_sign = "Gemini"
			elif ((int(dates[1])==6 and int(dates[0]) >= 21) or (int(dates[1])==7 and int(dates[0]) <= 22)): zodiac_sign = "Cancer"
			elif ((int(dates[1])==7 and int(dates[0]) >= 23) or (int(dates[1])==8 and int(dates[0]) <= 22)): zodiac_sign = "Leo"
			elif ((int(dates[1])==8 and int(dates[0]) >= 23) or (int(dates[1])==9 and int(dates[0]) <= 22)): zodiac_sign = "Virgo"
			elif ((int(dates[1])==9 and int(dates[0]) >= 23) or (int(dates[1])==10 and int(dates[0]) <= 22)): zodiac_sign = "Libra"
			elif ((int(dates[1])==10 and int(dates[0]) >= 23) or (int(dates[1])==11 and int(dates[0]) <= 21)): zodiac_sign = "Scorpio"
			elif ((int(dates[1])==11 and int(dates[0]) >= 22) or (int(dates[1])==12 and int(dates[0]) <= 21)): zodiac_sign = "Sagittarius"
			return zodiac_sign
	else: 
		return None

# Check if input is number
def checkInt(value):
	try:
		int(value)
		return True
	except:
		return False

# File upload handler
def uploadFile(fileInput, type, path, newName, newExt):
	upload = request.files.get(fileInput)
	# Checks if upload is not empty
	if upload != None:
		name, ext = os.path.splitext(upload.filename)
		# !!! Useless code?
		if type == 'image':
			extList = ('.png', '.jpg', '.jpeg')
		elif type == 'text':
			extList = ('.txt', 'doc', 'docx')
		# Builds path and name for file
		file_path = "static/{path}/{file}".format(path=path, file = "{0}{1}".format(newName, newExt))
		# Uploads file
		upload.save(file_path,overwrite=True)

# Spreads data to dictionary
def dataToDict(input):
	output = {}
	for x in input:
		# Saves all columns after primary key (id) to dictionary
		output[x[0]] = x[1:]
	return output

# Converts tags to links
def tagToLink(s, d):
	# Splits string with tag START to a list of strings
	txt = s.split("{user=")
	indexes = []
	# Splits list of strings with tag END and removes lists in list
	for x in enumerate(txt):
		txt[x[0]] = txt[x[0]].split("}")
		if len(txt[x[0]]) == 2:
			# Gets tag ID for further reference
			indexes.append((txt[x[0]])[0])
	# Replaces each tag
	for y in indexes:
		s = s.replace("{user="+ y + "}","<a href='/profile/" + y + "'>" + (d.get(int(y), "?"))[0] + "</a>")
	return s

## Server
# Home page
@app.route('/')
def index():
	# Gets data for table
	c.execute('SELECT user_id, name, met_how, met_when, bday, zodiac, gender FROM friends')
	a = dataToDict(c.fetchall())
	# Checks if database has any entries
	if len(a) != 0:
		# Gets data for table
		c.execute('SELECT * FROM metHow')
		b = dataToDict(c.fetchall())
		# Outputs table
		return template('view/header.html', title=l_title.get("myFriends", "???"), url=url, lan=l_header) + template('view/table.html', items=a, met=b, url=url, lan=l_table) + template('view/footer.html', lan=l_footer)
	else:
		# Outputs error
		return template('view/header.html', title=l_title.get("404", "???"), url=url, lan=l_header) + template('view/error.html', error=102, url=url, lan=l_error) + template('view/footer.html', lan=l_footer)

# Person profile
@app.route('/profile/<id>')
@app.route('/profile/<id>/')
def profile(id):
	# Gets URL variable save which is passed on line 107
	save = request.query.get('save')
	# Gets data for profile
	c.execute('SELECT * FROM friends WHERE user_id =' + id )
	a = c.fetchone()
	c.execute('SELECT how FROM metHow WHERE how_id=' + str(a[2]))
	b = [r[0] for r in c.fetchall()]
	# Checks if has profile picture
	if os.path.exists("static/avatar/" + str(id) + ".png"):
		# Generates path to profile picture
		path = "avatar/" + str(id) + ".png"
	else: 
		# Generates path to default picture
		path = "img/noProfile.svg"
	# Outputs profile
	return template('view/header.html', title=a[1].encode("UTF-8"), url=url, lan=l_header) + template('view/profile.html', msg=save, id=a[0], item=a, how=b[0], desc=a[7], url=url, path=path,lan=l_profile) + template('view/footer.html', lan=l_footer)

# Profile edit GET
@app.route('/profile/<id>/edit')
@app.route('/profile/<id>/edit/')
def editProfile(id):
	# Gets data for profile edit
	c.execute('SELECT * FROM friends WHERE user_id =' + id )
	a = c.fetchone()
	c.execute('SELECT * FROM metHow')
	b = dataToDict(c.fetchall())
	# Checks if has profile picture
	if os.path.exists("static/avatar/" + str(id) + ".png"):
		# Generates path to profile picture
		path = "avatar/" + str(id) + ".png"
	else: 
		# Generates path to default picture
		path = "img/noProfile.svg"
	# Outputs profile edit
	return template('view/header.html', title=a[1].encode("UTF-8"), url=url, lan=l_header) + template('view/profileEdit.html', id=a[0], item=a, url=url, metHow=b, path=path, lan=l_profile) + template('view/footer.html', lan=l_footer)

# Profile edit POST
@app.post('/profile/<id>/edit')
def saveProfile(id):
	# Gets data from each fields
	gender = str(request.POST.get('gender'))
	bday = str(request.forms.get('bday')).rstrip().lstrip()	
	met_how = request.forms.get('met_how')
	met_when = str(request.forms.get('met_when')).rstrip().lstrip()
	desc = request.forms.get('desc').rstrip().lstrip()
	# Checks if selected "other" in form field
	if met_how == "other":
		# Adds new entry to table
		newRow = str(request.forms.get('addNew'))
		c.execute("INSERT INTO metHow(how) VALUES(?)", [newRow])
		conn.commit()
		# Gets latest entry
		met_how = c.lastrowid
	else:
		# Gets selected item id
		met_how = int(met_how)
	# Upload picture
	uploadFile("upload", "image", "avatar", str(id), ".png")
	# Update profile
	c.execute("""UPDATE friends SET met_how = ?, met_when = ?, gender = ?, bday = ?, zodiac = ?, desc = ? WHERE user_id= ? """,
	(met_how,met_when,gender,bday,getZodiac(bday),desc,id))
	conn.commit()
	# Redirect to profile
	redirect('/profile/' + id + '?save=True')

# Profile delete GET
@app.route('/profile/<id>/delete')
@app.route('/profile/<id>/delete/')
def deleteProfile(id):
	confirm = request.query.get('confirm')
	if confirm == "True":
		c.execute('DELETE FROM friends WHERE user_id=' + id)
		conn.commit()
		redirect('/')
	else:
		c.execute('SELECT name FROM friends WHERE user_id = ' + id)
		a = (c.fetchone())[0]
		return template('view/header.html', title=a.encode("UTF-8"), url=url, lan=l_header) + template('view/profileDelete.html', id=id, name=a, url=url, lan=l_profileDel) + template('view/footer.html', lan=l_footer)

# Profile create GET
@app.route('/profile/create')
@app.route('/profile/create/')
def createProfile():
	c.execute('SELECT * FROM metHow')
	a = dataToDict(c.fetchall())
	return template('view/header.html', title=l_title.get("crtProf", "???"), url=url, lan=l_header) + template('view/profileCreate.html', url=url, metHow=a, lan=l_profile) + template('view/footer.html', lan=l_footer)

# Profile create POST
@app.post('/profile/create')
def create():
	name = str(request.forms.get('name')).rstrip().lstrip()
	gender = str(request.POST.get('gender'))
	bday = str(request.forms.get('bday')).rstrip().lstrip()	
	met_how = request.forms.get('met_how')
	met_when = str(request.forms.get('met_when')).rstrip().lstrip()
	desc = request.forms.get('desc').rstrip().lstrip()
	
	if met_how == "other":
		newRow = str(request.forms.get('addNew'))
		c.execute("INSERT INTO metHow(how) VALUES(?)", [newRow])
		conn.commit()
		met_how = c.lastrowid
	else:
		met_how = int(met_how)

	c.execute("INSERT INTO friends (name, met_how, met_when, bday, zodiac, gender, desc) VALUES (?, ?, ?, ?, ?, ?, ?)", 
			 (name, met_how, met_when, bday, getZodiac(bday), gender, desc))
	conn.commit()
	uploadFile("upload", "image", "avatar", str(c.lastrowid), ".png")
	redirect('/profile/' + str(c.lastrowid))

# Diary
@app.route('/diary')
@app.route('/diary/')
def diary():
	c.execute('SELECT * FROM diary')
	a = c.fetchall()
	c.execute('SELECT user_id, name FROM friends')
	b = dataToDict(c.fetchall())
	# Checks if database has any entries
	if len(a) != 0:
		# Displays entries
		return template('view/header.html', title=l_title.get("myDiary","???"), url=url, lan=l_header) + template('view/diary.html', names=b, articles=a, url=url, tagToLink=tagToLink) + template('view/footer.html', lan=l_footer)
	else:
		# Displays error
		return template('view/header.html', title=l_title.get("404","???"), url=url, lan=l_header) + template('view/error.html', error=101, url=url, lan=l_error) + template('view/footer.html', lan=l_footer)

# Diary article
@app.route('/diary/<id>')
@app.route('/diary/<id>/')
def articleDisplay(id):
	c.execute('SELECT title, article, date FROM diary WHERE article_id=' + id)
	a = (c.fetchall())[0]
	c.execute('SELECT user_id, name FROM friends')
	b = dataToDict(c.fetchall())
	return template('view/header.html', title=l_title.get("myDiary","???"), url=url, lan=l_header) + template('view/diaryDisplay.html', text=tagToLink(a[1], b), date=a[2], title=a[0], url=url, id=id) + template('view/footer.html', lan=l_footer)

# Diary article edit
@app.route('/diary/<id>/edit')
@app.route('/diary/<id>/edit/')
def articleEdit(id):
	c.execute('SELECT title, article, date FROM diary WHERE article_id=' + id)
	a = (c.fetchall())[0]
	c.execute('SELECT user_id, name FROM friends')
	b = dataToDict(c.fetchall())
	return template('view/header.html', title=l_title.get("myDiary","???"), url=url, lan=l_header) + template('view/diaryEdit.html', text=a[1], date=a[2], title=a[0], id=id,people=b, url=url, lan=l_diaryAC, textEditor=l_textEditor) + template('view/footer.html', lan=l_footer)

# Diary article save
@app.post('/diary/<id>/edit')
def articleSave(id):
	title = str(request.forms.get('title')).rstrip().lstrip()
	article = request.forms.get('article').rstrip().lstrip()
	c.execute('UPDATE diary SET title = ?, article = ? WHERE article_id = ?', (title, article, id))
	conn.commit()
	redirect('/diary/' + id)

# Diary delete article GET
@app.route('/diary/<id>/delete')
@app.route('/diary/<id>/delete/')
def articleDelete(id):
	confirm = request.query.get('confirm')
	if confirm == "True":
		c.execute('DELETE FROM diary WHERE article_id=' + id)
		conn.commit()
		redirect('/diary')
	else:
		c.execute('SELECT title FROM diary WHERE article_id = ' + id)
		a = (c.fetchone())[0]
		return template('view/header.html', title=a.encode("UTF-8"), url=url, lan=l_header) + template('view/diaryDelete.html', id=id, title=a, url=url, lan=l_diaryDel) + template('view/footer.html', lan=l_footer)

# Diary create article GET
@app.route('/diary/create')
@app.route('/diary/create/')
def articleCreate():
	c.execute('SELECT user_id, name FROM friends')
	a = dataToDict(c.fetchall())
	return template('view/header.html', title=l_title.get("myDiary","???"), url=url, lan=l_header) + template('view/diaryAdd.html', people=a, url=url, lan=l_diaryAC, textEditor=l_textEditor) + template('view/footer.html', lan=l_footer)

# Diary create article POST
@app.post('/diary/create')
def add():
	title = str(request.forms.get('title')).rstrip().lstrip()
	article = request.forms.get('article').rstrip().lstrip()
	c.execute('INSERT INTO diary (title, article, date) VALUES (?, ?, ?)', (title, article, time.strftime("%d.%m.%Y")))
	conn.commit()
	redirect('/diary/' + str(c.lastrowid))

# Settings GET
# @app.route('/settings')
# def settings(): return template('view/', url=url)

# Routing for static files
@app.route('/static/<filename:path>', name="static")
def static(filename): return static_file(filename, root='static/') 

# getLan()
app.run(host='localhost', port=8080)