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
import paho.mqtt.client
from core import *
import requests
from jwthelper import JwtHelper
import random
from threading import Thread

class ApiClient:
    #URI for server
    uri : str
    #secret given by server
    secret: str
    #taxi number
    taxi_id: str
    #ride id
    ride_id: str



    def __init__(self, uri: str, license: str, name: str, category: str):
        self.uri = uri
        self.license = license
        self.name = name
        self.category = category


    def register(self):
        print(f'registering new taxi for {self.license}')
        request_url = f'{self.uri}/register'
        payload = {'type': 'taxi', 'license': self.license, 'name': self.name, 'category': self.category}
        response = requests.request(method="POST", url=request_url, json=payload,
                                    headers={'Content-Type': 'application/json'})

        data: dict = response.json()
        self.taxi_id = data['taxi_id']
        self.secret = data['secret']
        print(f'{self.license} registered with user id {self.taxi_id} and secret {self.secret}')

    @classmethod
    def taxi_types(cls):
        return ['MINI', 'ECONOMY', 'SEDAN', 'LUXURY', 'ROYAL']

    def accept(self, ride_id):
        request_url = f'{self.uri}/accept'
        helper = JwtHelper(secret=self.secret)
        token = helper.create_jwt(identity=self.taxi_id, minutes=2)
        payload = {'taxi_id': self.taxi_id, 'ride_id': ride_id, 'accepted': random.choice(['YES', 'NO'])}
        requests.request(method="POST", url=request_url, json=payload,
                                    headers={'Content-Type': 'application/json',
                                             'X-Taxi-Id': self.taxi_id,
                                             'X-Token': token})
        print(f'Taxi accepted the ride request')




    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        payload = json.loads(msg.payload)
        if payload['type'] == 'ride_request':
            ride_id = payload['ride_id']
            self.accept(ride_id)

    def login(self):
        request_url = f'{self.uri}/login'
        helper = JwtHelper(secret=self.secret)
        token = helper.create_jwt(identity=self.taxi_id, minutes=2)
        payload = {'taxi_id': self.taxi_id}
        response = requests.request(method="POST", url=request_url, json=payload,
                                    headers={'Content-Type': 'application/json',
                                             'X-Taxi-Id': self.taxi_id,
                                             'X-Token': token})
        data: dict = response.json()
        print(f'Server responded with {data}')
        #return data
        def mqtt_listener(cl, ud, msg: paho.mqtt.client.MQTTMessage):
            print(msg.payload)
            print(self)

        # Listen for taxi request from user
        mqtt_client = MqttClient(name=self.name, host=data['host'])
        mqtt_client.connect()
        mqtt_client.subscribe(topic=data['topic'], fn=mqtt_listener)
        mqtt_client.block()

