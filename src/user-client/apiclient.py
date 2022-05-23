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

import requests
from jwthelper import JwtHelper


class ApiClient:
    # URI for server
    uri: str
    # Secret given by server
    secret: str
    # user id given by server
    user_id: str
    # name of the user
    name: str

    def __init__(self, uri: str, name: str):
        self.uri = uri
        self.name = name

    def register(self):
        print(f'registering a new user for {self.name}')
        request_url = f'{self.uri}/register'
        payload = {"type": "user", "name": self.name}
        response = requests.request(method="POST", url=request_url, json=payload,
                                    headers={'Content-Type': 'application/json'})
        data: dict = response.json()
        self.user_id = data['user_id']
        self.secret = data['secret']
        print(f'{self.name} registered with user id {self.user_id} and secret {self.secret}')

    def find_taxi(self, latitude, longitude):
        print(f'{self.user_id}/{self.name} trying to find a taxi from location {latitude} and {longitude}')
        request_url = f'{self.uri}/findtaxi'
        helper = JwtHelper(secret=self.secret)
        token = helper.create_jwt(identity=self.user_id, minutes=2)
        payload = {'location': [latitude, longitude]}
        response = requests.request(method="POST", url=request_url, json=payload,
                                    headers={'Content-Type': 'application/json',
                                             'X-User-Id': self.user_id,
                                             'X-Token': token})
        data: dict = response.json()
        print(f'Server responded with {data}')
