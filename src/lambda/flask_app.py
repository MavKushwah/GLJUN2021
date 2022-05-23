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

# Flask constructor takes the name of
# current module (__name__) as argument.

app = Flask(__name__)


# Handle accept Call
@app.route('/accept', methods=['POST'])
def accept():
    from accept import handler
    return run_event(handler, get_event(request))


# Handle cleanup Call
@app.route('/cleanup', methods=['POST'])
def cleanup():
    from cleanup import handler
    return run_event(handler, get_event(request))


# Handle find_taxi Call
@app.route('/findtaxi', methods=['POST'])
def find_taxi():
    from find_taxi import handler
    return run_event(handler, get_event(request))


# Handle location Call
@app.route('/location', methods=['POST'])
def location():
    from location import handler
    return run_event(handler, get_event(request))


# Handle Login Call
@app.route('/login', methods=['POST'])
def login():
    from login import handler
    return run_event(handler, get_event(request))


# Handle logoff Call
@app.route('/logoff', methods=['POST'])
def logoff():
    from logoff import handler
    return run_event(handler, get_event(request))


# Handle register Call
@app.route('/register', methods=['POST'])
def register():
    from register import handler
    return run_event(handler, get_event(request))


# Handle ride Call
@app.route('/ride', methods=['POST'])
def ride():
    from ride import handler
    return run_event(handler, get_event(request))


def run_event(fn, event):
    r = fn(event, None)
    resp = make_response(json.dumps(r['body']), r['statusCode'])
    resp.headers.update(r['headers'])
    return resp


def get_event(r: Request) -> dict:
    event: dict = dict()
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
