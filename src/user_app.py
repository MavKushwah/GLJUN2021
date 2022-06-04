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
from random import uniform
import argparse
from src.clients.user.apiclient import ApiClient
from threading import Thread


# Initializing Parser
parser = argparse.ArgumentParser(description='User Registration')

#Adding argument
parser.add_argument('--count', type=int, help='user count')
parser.add_argument('--uri', type=str, help='server uri')
parser.add_argument('--latitude', type=int, nargs='+', help='min and max latitude')
parser.add_argument('--longitude', type=int, nargs='+', help='min and max longitude')
args = parser.parse_args()

user_count = args.count
server_uri = args.uri
min_latitude = args.latitude[0]
max_latitude = args.latitude[1]
min_longitude = args.longitude[0]
max_longitude = args.longitude[1]


user_list = list()

for index in range(0, user_count):
    name = f'taxi user {index}'
    client = ApiClient(uri=server_uri, name=name)
    client.register()
    user_list.append(client)

for user in user_list:
    print(user)
    latitude, longitude = uniform(min_latitude, max_latitude), uniform(min_longitude, max_longitude)
    t = Thread(target=client.createride, kwargs={'user_id': user, 'longitude': longitude, 'latitude': latitude})
    t.start()


