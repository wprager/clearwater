from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask.ext.login import LoginManager, current_user, login_required, login_user, logout_user

from clearwater import app
import constants
from models import User, Measurement, login_serializer

import csv
from datetime import datetime
import json
import md5
from urlparse import urlparse, urljoin
from werkzeug import secure_filename

app.secret_key = 'secret_key'
lm = LoginManager()
lm.init_app(app)

# TODO: allow users to register?

# -----------------------------------------------
# LOGIN MANAGER CONFIG
# -----------------------------------------------
lm.login_view = 'index'
lm.login_message_category = 'info'
# lm.refresh_view = 'reauthenticate'

@lm.user_loader
def load_user(userid):
	return User.get(userid)

@lm.token_loader
def load_token(token):
	max_age = app.config['REMEMBER_COOKIE_DURATION'].total_seconds()
	data = login_serializer.loads(token, max_age=max_age)
	user = User.get(data[0])
	if user and data[1] == user.password:
		return user
	return None

# -----------------------------------------------
# UTIL
# -----------------------------------------------
def hash_pass(password):
	saltedPass = password + app.secret_key
	return md5.new(saltedPass).hexdigest()

def is_safe_url(target):
	base_url = urlparse(request.host_url)
	requested_url = urlparse(urljoin(request.host_url, target))
	return requested_url.scheme in ('http', 'https') and base_url.netloc == requested_url.netloc

# -----------------------------------------------
# ROUTES
# -----------------------------------------------
@app.route('/')
def index():
	if current_user.is_anonymous():
		return render_template('login.html', nxt=request.args.get('next'))
	else:
		return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return redirect(url_for('index'))
	elif request.method == 'POST':
		u = str(request.form['username'])
		p = str(request.form['password'])
		user = User.get(u)
		
		if user:
			if user.password == hash_pass(p):
				login_user(user, remember=('rememberme' in request.form))
			else:
				flash(constants.INVALID_PASSWORD, 'danger')
		else:
			flash(constants.INVALID_USERNAME, 'danger')
		
		# may still be vulnerable to open redirects (try http://localhost:5000/?next=////google.com)
		# check http://homakov.blogspot.com/2014/01/evolution-of-open-redirect-vulnerability.html
		if is_safe_url(request.form['next']):
			return redirect(request.form['next'] or url_for('index'))
		else:
			return abort(400)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

# TODO: add /users/<int:userid> GET? for user profiles & easier edit operations?
@app.route('/users', methods=['GET', 'POST'])
@login_required
def manageUsers():
	if request.method == 'GET':
		users = User.getAll()
		return render_template('users.html', users=users)
	elif request.method == 'POST':
		if not current_user.isAdmin():
			flash(constants.NOT_ALLOWED, 'danger')
			return redirect(url_for('manageUsers'))
		else:
			u = str(request.form['username'])
			p = str(request.form['password'])
			user = User.get(u)
			if user:
				flash(constants.USERNAME_TAKEN, 'danger')
			else:
				User.create(User(u, hash_pass(p)))
				flash(constants.USER_CREATE_SUCCESS.format(u), 'success')
		return redirect(url_for('manageUsers'))

@app.route('/user-delete', methods=['POST'])
@login_required
def deleteUser():
	if not current_user.isAdmin():
		flash(constants.NOT_ALLOWED, 'danger')
	else:
		userid = unicode(request.form['userid'])
		user = User.get(userid)
		User.delete(user)
		flash(constants.USER_DELETE_SUCCESS.format(user.username), 'success')
	return redirect(url_for('manageUsers'))

# TODO: add /measurements/<int:measurementid> edits?
@app.route('/measurements', methods=['GET', 'POST'])
@login_required
def manageMeasurements():
	if request.method == 'GET':
		measurements = Measurement.getAll()
		users = {}
		for user in User.getAll():
			users[user.id] = user.username
		return render_template('measurements.html', measurements=measurements, users=users)
	elif request.method == 'POST':
		month = request.form['month']
		day = request.form['day']
		year = request.form['year']
		hour = request.form['hour']
		minute = request.form['minute']
		second = request.form['second']
		ampm = request.form['ampm']
		if ampm == 'am' and hour == '12':
			hour = '00'
		elif ampm == 'pm' and hour != '12':
			hour = str(int(hour) + 12)
		try:
			t = datetime.strptime(' '.join([month, day, year, hour, minute, second]), '%m %d %Y %H %M %S')
		except ValueError:
			flash(constants.DATE_OUT_OF_RANGE, 'danger')
			return redirect(url_for('manageMeasurements'))
		
		# t = request.form['time']
		# try:
		# 	t = datetime.strptime(t, '%Y-%m-%dT%H:%M:%S')
		# except ValueError:
		# 	try:
		# 		t = datetime.strptime(t, '%Y-%m-%dT%H:%M')
		# 	except ValueError:
		# 		flash(constants.INVALID_DATE, 'danger')
		# 		return redirect(url_for('manageMeasurements'))
		
		p = float(request.form['ph'])
		measurement = Measurement.get(t)
		if measurement:
			flash(constants.TIME_TAKEN, 'danger')
		else:
			Measurement.create(Measurement(current_user.id, t, p))
			flash(constants.MEASUREMENT_CREATE_SUCCESS, 'success')
		return redirect(url_for('manageMeasurements'))

@app.route('/measurement-delete', methods=['POST'])
@login_required
def deleteMeasurement():
	if not current_user.isAdmin():
		flash(constants.NOT_ALLOWED, 'danger')
	else:
		measurementid = unicode(request.form['measurementid'])
		Measurement.delete(Measurement.get(measurementid))
		flash(constants.MEASUREMENT_DELETE_SUCCESS, 'success')
	return redirect(url_for('manageMeasurements'))

@app.route('/csv-upload', methods=['POST'])
@login_required
def csvUpload():
	file = request.files['csv']
	badSyntax = []
	timeTaken = []
	if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() == 'csv':
		filename = secure_filename(file.filename)
		try:
			with open(filename, 'r') as csvFile:
				reader = csv.reader(csvFile)
				headers = reader.next()
				if len(headers) == 2 and headers[0].lower() == 'time' and headers[1].lower() == 'ph':
					for row in reader:
						if len(row) == 2:
							t = row[0]
							try:
								t = datetime.strptime(t, '%Y-%m-%dT%H:%M:%S')
							except ValueError:
								try:
									t = datetime.strptime(t, '%Y-%m-%dT%H:%M')
								except ValueError:
									badSyntax.append(reader.line_num)
									continue
							
							p = row[1]
							try:
								p = float(p)
								if not (0 <= p <= 14):
									raise ValueError
							except ValueError:
								badSyntax.append(reader.line_num)
								continue
							
							measurement = Measurement.get(t)
							if measurement:
								timeTaken.append(reader.line_num)
								continue
							Measurement.create(Measurement(current_user.id, t, p))
						else:
							badSyntax.append(reader.line_num)
					
					flash(constants.CSV_UPLOAD_SUCCESS, 'success')
					if badSyntax:
						flash(constants.CSV_BAD_SYNTAX.format(json.dumps(badSyntax)), 'info')
					if timeTaken:
						flash(constants.CSV_TIME_TAKEN.format(json.dumps(timeTaken)), 'info')
				else:
					flash(constants.INVALID_CSV_HEADER, 'danger')
		except IOError:
			flash(constants.INVALID_CSV_FILE, 'danger')
	else:
		flash(constants.INVALID_CSV_FILE, 'danger')
	
	return redirect(url_for('manageMeasurements'))


@app.errorhandler(400)
def badRequest(error):
	return render_template('400.html'), 400

@app.errorhandler(404)
def notFound(error):
	return render_template('404.html'), 404

@app.errorhandler(413)
def requestTooLarge(error):
	return render_template('413.html'), 413
