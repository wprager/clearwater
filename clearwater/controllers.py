from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask.ext.login import LoginManager, current_user, login_required, login_user, logout_user
from clearwater import app
from models import User, Measurement, login_serializer
from datetime import datetime
import md5

app.secret_key = 'secret_key'
lm = LoginManager()
lm.init_app(app)

# TODO: create separate i18n file containing strings/flash messages

# -----------------------------------------------
# LOGIN MANAGER CONFIG
# -----------------------------------------------
lm.login_view = 'index'
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
				# TODO: validate the 'next' parameter (protect from "open redirect" vulnerability)
			else:
				flash('Invalid password.', 'danger')
		else:
			flash('Invalid username.', 'danger')
		
		if request.form['next'] != 'None':
			return redirect(str(request.form['next']))
		else:
			return redirect(url_for('index'))

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
			flash('You are not allowed to perform that action.', 'danger')
			return redirect(url_for('manageUsers'))
		else:
			u = str(request.form['username'])
			p = str(request.form['password'])
			user = User.get(u)
			if user:
				flash('Username already taken', 'danger')
			else:
				User.create(User(u, hash_pass(p)))
				flash('Successfully created user: "' + u + '"', 'success')
		return redirect(url_for('manageUsers'))

@app.route('/user-delete', methods=['POST'])
@login_required
def deleteUser():
	if not current_user.isAdmin():
		flash('You are not allowed to perform that action.', 'danger')
	else:
		userid = unicode(request.form['userid'])
		User.delete(User.get(userid))
		flash('Successfully deleted user: "' + user.username + '"', 'success')
	return redirect(url_for('manageUsers'))

# TODO: add /measurements/<int:measurementid> edits?
@app.route('/measurements', methods=['GET', 'POST'])
@login_required
def manageMeasurements():
	if request.method == 'GET':
		measurements = Measurement.getAll()
		return render_template('measurements.html', measurements=measurements)
	elif request.method == 'POST':
		# TODO: add ways to do this in bulk - csv upload? parse json info over network?
		t = request.form['time']
		t = datetime.strptime(t, '%Y-%m-%dT%H:%M')
		p = str(request.form['ph'])
		measurement = Measurement.get(t)
		if measurement:
			flash('Measurement already taken at that time', 'danger')
		else:
			Measurement.create(Measurement(t, p))
			flash('Successfully created measurement', 'success')
		return redirect(url_for('manageMeasurements'))

@app.route('/measurement-delete', methods=['POST'])
@login_required
def deleteMeasurement():
	if not current_user.isAdmin():
		flash('You are not allowed to perform that action.', 'danger')
	else:
		measurementid = unicode(request.form['measurementid'])
		Measurement.delete(Measurement.get(measurementid))
		flash('Successfully deleted measurement.', 'success')
	return redirect(url_for('manageMeasurements'))
