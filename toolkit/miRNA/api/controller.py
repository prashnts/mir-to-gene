#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#.--. .-. ... .... -. - ... .-.-.- .. -.

from flask import Flask, Blueprint
from flask_restful import Resource, Api

from flask.ext.mongorest import MongoRest
from flask.ext.mongorest.views import ResourceView
from flask.ext.mongorest import methods

from miRNA.polynucleotide.controller import GeneResource, miRNAResource
from miRNA.graph.controller import SubGraphController
from miRNA.search.controller import SearchController
from miRNA import app, db

api = Blueprint('api', __name__)

mongo_rest = MongoRest(app, url_prefix = '/api')
restful = Api(app, prefix = '/api')

@mongo_rest.register(name = 'gene', url = '/gene/')
class GeneRest(ResourceView):
  resource = GeneResource
  methods = [methods.Fetch]

@mongo_rest.register(name = 'miRNA', url = '/mirna/')
class miRNAREST(ResourceView):
  resource = miRNAResource
  methods = [methods.Fetch]

restful.add_resource(SearchController, '/search')
restful.add_resource(SubGraphController, '/graph')
