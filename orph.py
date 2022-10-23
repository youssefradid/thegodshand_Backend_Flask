from setup import create_app, db
from setup.models import User, Orphanage, Message, Donation
from flask import Flask,redirect
from flask_cors import CORS

application = create_app()
CORS(application)

@application.route('/')
def home():
     return redirect('/index.html')

# the decorator below registers the function as a shell context function
@application.shell_context_processor 
def make_shell_context():
    return {'db': db,'User': User, 'Orphanage': Orphanage, 'Message': Message, 'Donation': Donation}