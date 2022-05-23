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
import random
from random import uniform

from apiclient import ApiClient

USER_COUNT = 20
MAX_LATITUDE = 60
MAX_LONGITUDE = 60
SERVER_URI = 'http://127.0.0.1:5000'

user_list = list()

for index in range(0, USER_COUNT):
    name = f'taxi user {index}'
    client = ApiClient(uri=SERVER_URI, name=name)
    client.register()
    latitude, longitude = uniform(-180, 180), uniform(-90, 90)
    client.find_taxi(latitude, longitude)
    user_list.append(client)
