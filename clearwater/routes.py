from flask import Flask
from clearwater import app

@app.route('/')
def hello():
	return 'hello world!'
