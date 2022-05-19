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
import json
import random

import paho.mqtt.client
from paho.mqtt import client as mqtt_client


class MqttClient:

    # host
    host: str
    # port
    port: int
    # client-id
    client_id: object
    # client
    client: paho.mqtt.client.Client

    def __init__(self, host: str, port: int = 1883):
        self.host = host
        self.port = port
        self.client_id = f'python-mqtt-{random.randint(0, 1000)}'

    def connect(self):
        client = mqtt_client.Client(self.client_id)
        client.connect(self.host, self.port)
        self.client = client

    def send_to_taxi(self, taxi_uuid: str, message: dict):
        print(f'sending message to taxi topic {taxi_uuid} {json.dumps(message)}')
        self.client.publish(topic=f'taxi/{taxi_uuid}', payload=json.dumps(message))
