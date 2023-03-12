#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
from flask import Flask, request
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
import json
app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()
        # self.modified = datetime.now() 

    def update(self, entity, key, value):
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        self.space[entity] = data

    def clear(self):
        self.space = dict()

    def get(self, entity):
        return self.space.get(entity,dict())
    
    def world(self):
        return self.space
    
    def __repr__(self) -> str:
        return str(self.space)

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}' 

myWorld = World()       
modified = None   

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])

@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''
    return flask.redirect("./static/index.html", 301)

@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''update the entities via this interface'''
    json = flask_post_json()
    # Change the modified date as well
    if request.method == "PUT":
        try:
            for key in json:
                value = json[key]
                myWorld.update(entity, key, value)
                modified = datetime.now()
        except:
            return {"message":"Bad request"}, 400
    elif request.method == "POST":
        try:
            myWorld.set(entity, json['entity'])
            modified = datetime.now()
        except Exception as e:
            print(e)
            return {"message":"Bad request"}, 400

    return flask.jsonify(json), 200

@app.route("/world", methods=['POST','GET'])    
def world():
    '''you should probably return the world here'''
    return flask.jsonify(myWorld.world()), 200
    


@app.route("/entity/<entity>")    
def get_entity(entity):
    '''This is the GET version of the entity interface, return a representation of the entity'''
    
    
    response =  flask.jsonify(myWorld.get(entity))
    stamp = mktime(modified.timetuple())
    response.headers['Last-Modified'] = \
        format_date_time(stamp)
    print(response.headers['Last-Modified'])
    return response, 200

@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world out!'''
    if request.method == "GET":
        return {"message": "Bad Request"}, 400
    myWorld.clear()
    return {"message": "Cleared world"}, 200

if __name__ == "__main__":
    app.run()
