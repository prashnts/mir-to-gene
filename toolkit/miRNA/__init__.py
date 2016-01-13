#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask import Flask, render_template
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__, template_folder='static')
app.config.from_pyfile('config.py')

db = MongoEngine(app)

def create_app():
  from .admin.controller import admin
  from .api.controller import api

  app.register_blueprint(api, url_prefix = '/api')

  @app.route('/')
  def home():
    return render_template('index.html')