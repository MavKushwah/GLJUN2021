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
from typing import Optional

import requests

from .jwthelper import JwtHelper


class HttpClient:

    def __init__(self, uri: str):
        self.uri = uri

    def send_taxi_request(self, path: str, identity: str, secret: str, body: Optional[dict]):
        request_url = f'{self.uri}{path}'
        helper = JwtHelper(secret=secret)
        token = helper.create_jwt(identity=identity, minutes=2)
        response = requests.request(method="POST", url=request_url, json=body,
                                    headers={'Content-Type': 'application/json',
                                             f'X-Taxi-Id': identity,
                                             'X-Token': token})
        return self.__handle_response(response)

    def send_user_request(self, path: str, identity: str, secret: str, body: Optional[dict]):
        request_url = f'{self.uri}/{path}'
        helper = JwtHelper(secret=secret)
        token = helper.create_jwt(identity=identity, minutes=2)
        response = requests.request(method="POST", url=request_url, json=body,
                                    headers={'Content-Type': 'application/json',
                                             f'X-User-Id': identity,
                                             'X-Token': token})
        return self.__handle_response(response)

    def send_anonymous(self, path: str, body: Optional[dict]):
        request_url = f'{self.uri}/{path}'
        response = requests.request(method="POST", url=request_url, json=body,
                                    headers={'Content-Type': 'application/json'})
        return self.__handle_response(response)

    @classmethod
    def __handle_response(cls, response):
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.text)
