#!/usr/bin/env python

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from uuid import uuid4
from os import environ
from datetime import datetime
from config import DB_URL


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
db = SQLAlchemy(app)

class Message(db.Model):
  pk = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String())
  channel = db.Column(db.String())
  message = db.Column(db.String())
  timestamp = db.Column(db.DateTime())

  def __init__(self, username, message, timestamp, channel):
    self.username = username
    self.message = message
    self.timestamp = timestamp
    self.channel = channel



@app.route('/', methods=['GET', 'PUT'])
def search():

    filters = []
    requested_channel = request.args.get('channel')
    requested_user = request.args.get('user')
    query_string = request.args.get('q') or ''
    if requested_channel:
      filters.append(Message.channel == requested_channel)
    if requested_user:
      filters.append(Message.username == requested_user)
    if query_string:
      filters.append(Message.message.like('%{}%'.format(query_string)))

    results = Message.query.filter(and_(*filters)).order_by(Message.timestamp).all()

    channels = [x[0] for x in db.session.query(Message.channel.distinct()).order_by(Message.channel).all()]
    users = [x[0] for x in db.session.query(Message.username.distinct()).order_by(Message.username).all()]

    return render_template('search.html', 
                           results=results, 
                           channels=channels, 
                           users=users, 
                           requested_channel=requested_channel, 
                           requested_user=requested_user, 
                           query=query_string)


if __name__ == '__main__':
    app.run(debug=True)