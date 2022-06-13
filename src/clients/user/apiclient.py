#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Restricted Software.
# Copyright (c) 2022 My Great Learning.
# All Rights Reserved.
#
# @author Drisya Mathilakath
# @since 2022.05
#
import json
import random

import paho

from core import *


class UserApiClient:
    # URI for server
    server_client: HttpClient
    # Secret given by server
    secret: str
    # name of the user
    name: str
    # user id
    user_id: str
    # topic
    topic: str
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
    # taxi type
    taxi_type: str

    def __init__(self, uri: str, name: str, bound: LocationBound):
        self.server_client = HttpClient(uri=uri)
        self.name = name
        self.bound = bound
        self.ride_in_progress = False
        self.ride_remaining = 5
        taxi_types = list(['ALL'])
        taxi_types.extend(TAXI_TYPES)
        self.taxi_type = random.choice(taxi_types)
        self.log = Log(name=f'{name}/{self.taxi_type}')

    def send_authenticated(self, path: str, body):
        return self.server_client.send_user_request(path, self.user_id, self.secret, body)

    def register(self):
        self.log.log('registering this user with server')
        payload = {
            "type": "user",
            "name": self.name
        }
        data: dict = self.server_client.send_anonymous('register', payload)
        self.user_id = data['user_id']
        self.secret = data['secret']
        self.log.log('registered user: id={} secret={}', self.user_id, self.secret)

    def ride(self):
        current_latitude = random.uniform(self.bound.min_latitude, self.bound.max_latitude)
        current_longitude = random.uniform(self.bound.min_longitude, self.bound.max_longitude)
        self.log.log('create ride request: location={}, {} type={}', current_longitude, current_latitude,
                     self.taxi_type)
        payload = {'location': [current_longitude, current_latitude], 'type': self.taxi_type}
        data: dict = self.send_authenticated('createride', payload)

        ride_topic = data.get('topic')
        mqtt_host = data.get('host')
        ride_id = data.get('ride_id')
        self.log.log('ride request accepted: topic={} host={} ride_id={}', ride_topic, mqtt_host, ride_id)

        # subscribe to topic
        mqtt_client = MqttClient(host=mqtt_host, name=self.name)
        mqtt_client.connect()

        # handler for message
        def message_responder(client, userdata, message):
            self.ride_request_handler(mqtt_client, message)

        # wait for responses
        mqtt_client.subscribe(fn=message_responder, topic=ride_topic)
        mqtt_client.client.loop_start()
        # lets find taxi!
        try:
            data: dict = self.send_authenticated('findtaxi', data)
            if data.get('success'):
                self.log.log('taxi allocated for the ride: taxi_id={}', data.get('taxi_id'))
            else:
                self.log.log('taxi allocation failed for ride: ride_id={} msg={}', ride_id, data.get('msg'))

        finally:
            mqtt_client.client.loop_stop()
            mqtt_client.close()

    def ride_request_handler(self, mqtt_client: MqttClient, message: paho.mqtt.client.MQTTMessage):
        body: dict = json.loads(message.payload)
        if body.get("type") == "message":
            self.log.log('message from server: {}', body.get('msg'))
            return
        if body.get('completed'):
            self.log.log('ride request has been served by server: ride_id={}', body.get('ride_id'))
            mqtt_client.close()
            return
        self.log.log('unhandled message from server: {}', body)
