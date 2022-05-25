#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Restricted Software.
# Copyright (c) 2022 My Great Learning.
# All Rights Reserved.
#
# @author Anirudh Kushwah
# @since 2022.05
#
# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
import json

from flask import Flask, request, Request, make_response

from core import JwtHelper

# flask app
app = Flask(__name__)


# Handle accept Call
@app.route('/accept', methods=['POST'])
def accept():
    from functions.accept import handler
    return run_event(handler, get_event(request))


# Handle cleanup Call
@app.route('/cleanup', methods=['POST'])
def cleanup():
    from functions.cleanup import handler
    return run_event(handler, get_event(request))


# Handle create ride
@app.route('/createride', methods=['POST'])
def create_ride():
    from functions.createride import handler
    return run_event(handler, get_event(request))


# Handle find_taxi Call
@app.route('/findtaxi', methods=['POST'])
def find_taxi():
    from functions.find_taxi import handler
    return run_event(handler, get_event(request))


# Handle location Call
@app.route('/location', methods=['POST'])
def location():
    from functions.location import handler
    return run_event(handler, get_event(request))


# Handle Login Call
@app.route('/login', methods=['POST'])
def login():
    from functions.login import handler
    return run_event(handler, get_event(request, skip_body=True))


# Handle logoff Call
@app.route('/logoff', methods=['POST'])
def logoff():
    from functions.logoff import handler
    return run_event(handler, get_event(request, skip_body=True))


# Handle register Call
@app.route('/register', methods=['POST'])
def register():
    from functions.register import handler
    return run_event(handler, get_event(request))


# Handle ride Call
@app.route('/ride', methods=['POST'])
def ride():
    from functions.ride import handler
    return run_event(handler, get_event(request))


# Utility Calls
@app.route('/token', methods=['POST'])
def token():
    data: dict = request.get_json()
    taxi_id = data['taxi_id']
    secret = data['secret']
    helper = JwtHelper(secret=secret)
    j_token = helper.create_jwt(identity=taxi_id, minutes=5)
    return j_token, 200


def run_event(fn, event):
    r = fn(event, None)
    resp = make_response(r['body'], r['statusCode'])
    # resp.headers.update(r['headers'])
    for k, v in r['headers'].items():
        resp.headers.set(k, v)
    return resp


def get_event(r: Request, skip_body: bool = False) -> dict:
    event: dict = dict()
    if skip_body:
        event['body'] = ""
    else:
        event['body'] = json.dumps(request.get_json())
    event['isBase64Encoded'] = False
    heads = dict()
    for k in request.headers.keys():
        heads[k] = request.headers.get(k)
    event['headers'] = heads
    return event


# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()
