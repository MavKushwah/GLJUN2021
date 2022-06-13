#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Restricted Software.
# Copyright (c) 2022 My Great Learning.
# All Rights Reserved.
#
# @author
# @since 2022.05
#
import json
import random
import threading
import time

import paho.mqtt.client

from core import *


class TaxiApiClient:
    # URI for server
    server_client: HttpClient
    # Secret given by server
    secret: str
    # taxi id given by server
    taxi_id: str
    # name of the user
    name: str
    # license
    license: str
    # type
    taxi_type: str
    # topic
    topic: str
    # mqtt host
    mqtt_host: str
    # mqtt client
    mqtt_client: MqttClient
    # logger
    log: Log
    # location box
    bound: LocationBound
    # are you in middle of ride
    ride_in_progress: bool
    # ride count
    ride_remaining: int
    # Driver name
    driver_name: str

    def __init__(self, uri: str, name: str, license: str, taxi_type: str, bound: LocationBound, driver_name: str):
        self.server_client = HttpClient(uri=uri)
        self.name = name
        self.license = license
        self.taxi_type = taxi_type
        self.bound = bound
        self.ride_in_progress = False
        self.ride_remaining = 5
        self.log = Log(name=name)
        self.driver_name = driver_name

    '''
    def __init__(self, uri: str, taxi_id: str, secret: str):
        self.taxi_id = taxi_id
        self.server_client = HttpClient(uri=uri)
        self.secret = secret
    '''

    def send_authenticated(self, path: str, body):
        return self.server_client.send_taxi_request(path, self.taxi_id, self.secret, body)

    def register(self):
        self.log.log('registering this taxi with server')
        current_latitude = random.uniform(self.bound.min_latitude, self.bound.max_latitude)
        current_longitude = random.uniform(self.bound.min_longitude, self.bound.max_longitude)
        payload = {
            "type": "taxi",
            "name": self.name,
            "taxi_type": self.taxi_type,
            "license": self.license,
            "driver_name": self.driver_name,
            "location": {"type": "Point", "coordinates": [current_longitude, current_latitude]},
            "registered_on": time.time(),
            "last_updated_time": time.time()
        }
        data: dict = self.server_client.send_anonymous('register', payload)
        self.taxi_id = data['taxi_id']
        self.secret = data['secret']
        self.log.log('registered taxi: id={} secret={}', self.taxi_id, self.secret)

    def logoff(self):
        self.log.log('sending log off request to server')
        data: dict = self.send_authenticated('logoff', None)
        self.log.log('server response to log off request: {}', data)
        self.mqtt_client.close()

    def send_location(self, latitude, longitude):
        self.log.log('sending location update: {}, {}', longitude, latitude)
        data: dict = self.send_authenticated('location', {'location': [longitude, latitude]})
        self.log.log('server response to location request: {}', data)

    # handler for the message communication from server
    def ride_request_handler(self, message: paho.mqtt.client.MQTTMessage):
        # get the message count
        body: dict = json.loads(message.payload)
        self.log.log('mqtt-message: {}', body)
        message_type: str = body.get('type')
        if message_type == 'ride_request':
            accept: bool = random.randint(0, 11) < 9
            body['accepted'] = accept
            time.sleep(random.randint(1, 5))
            success: dict = self.send_authenticated('accept', body)
            if accept and success.get('success'):
                self.ride_remaining = self.ride_remaining - 1
                self.log.log('ride request {} was assigned to this taxi {}', body.get("ride_id"), self.taxi_id)
                # wait for a few seconds
                time.sleep(random.randint(1, 5))
                self.log.log('starting the ride {} on this taxi', body.get('ride_id'))
                start = {'action': 'start', 'ride_id': body.get('ride_id')}
                self.send_authenticated('ride', start)
                # wait for a few more seconds
                time.sleep(random.randint(5, 30))
                self.log.log('ending the ride {} on this taxi', body.get('ride_id'))
                stop = {'action': 'end', 'ride_id': body.get('ride_id')}
                self.send_authenticated('ride', stop)
            elif accept and not success.get('success'):
                self.log.log('ride request {} was assigned to someone else', body.get("ride_id"))
            elif not accept:
                self.log.log('rejecting this ride request {}', body.get("ride_id"))
        else:
            self.log.log('got message from server {}', body.get('msg'))
        if self.ride_remaining <= 0:
            self.log.log('no more remaining rides, time to say goodbye')
            self.logoff()

    def start_moving(self):
        count = 0
        current_latitude = random.uniform(self.bound.min_latitude, self.bound.max_latitude)
        current_longitude = random.uniform(self.bound.min_longitude, self.bound.max_longitude)
        while count < 1000:
            self.send_location(current_latitude, current_longitude)
            time.sleep(random.randint(15, 30))
            # latitude
            current_latitude = current_latitude + random.uniform(-0.005, 0.005)
            current_longitude = current_longitude + random.uniform(-0.005, 0.005)
            # increment the count
            count = count + 1
        self.mqtt_client.close()

    def start(self) -> None:
        self.log.log('sending a login request to server')
        data: dict = self.server_client.send_taxi_request('login', self.taxi_id, self.secret, None)
        self.mqtt_host = data['host']
        self.topic = data['topic']
        self.log.log('login response: host={} topic={}', self.mqtt_host, self.topic)

        # Create a responder
        def message_responder(client, userdata, message):
            self.ride_request_handler(message)

        # create a client to listen messages
        self.mqtt_client = MqttClient(name=self.name, host=self.mqtt_host)
        self.mqtt_client.connect()
        self.mqtt_client.subscribe(topic=self.topic, fn=message_responder)
        # start a thread to publish locations
        threading.Thread(target=self.start_moving).start()
        # start reading
        self.mqtt_client.block()
