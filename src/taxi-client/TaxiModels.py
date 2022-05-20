#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Restricted Software.
# Copyright (c) 2021 Great Learning.
# All Rights Reserved.
#
# @author Nilotpal Sarkar
# @since 2022.05
#
import datetime
import json
import random
from typing import List

import boto3
import geojson
from geojson import Point


class Taxi:
    def __init__(self, id, driver_name, type, vehicle_number, current_location, timestamp):
        self._id = id
        self.driver_name = driver_name
        self.type = type
        self.vehicle_number = vehicle_number
        self.location = current_location
        self.last_updated_time = timestamp

    def __str__(self) -> str:
        return f"id={self._id}, driver_name={self.driver_name}, type={self.type}, vehicle_number={self.vehicle_number}, location={self.location}, last_updated_time={self.last_updated_time} "

    @property
    def id(self):
        return self._id


class Taxi_Status:
    def __init__(self, taxi_id, location: Point, state, riding_with):
        self._id = id
        self.state = state
        self.taxi_id = taxi_id
        self.location = location
        self.riding_with = riding_with


class RandomLocationGenerator:
    def __init__(self, boundary: [], incrementBy: float):
        x1 = boundary[0]
        y1 = boundary[1]
        x2 = boundary[2]
        y2 = boundary[3]
        self.last_location = geojson.Point((random.uniform(x1, x2),
                                            random.uniform(y1, y2)))
        self.incrementBy = incrementBy

    def getNextLocation(self) -> Point:
        last_location: Point = self.last_location['coordinates']
        current_location = self.__update(last_location, self.incrementBy)
        self.last_location = current_location
        return current_location

    def __update(self, last_location: Point, incrementBy: float) -> Point:
        add = lambda location: location + incrementBy
        sub = lambda location: location - incrementBy
        noChange = lambda location: location
        formula: List = [add, sub, noChange]

        lon = last_location[0]
        lon = random.choice(formula)(lon)

        lat = last_location[1]
        lat = random.choice(formula)(lat)

        return Point((lon, lat))


class TaxiLocationPublisher:
    def __init__(self, snsTopic):
        self.client = boto3.client("sns",
                                             aws_access_key_id="AKIAWZKNZ2C7VEYGK57P",
                                             aws_secret_access_key="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",
                                             region_name="us-east-1"
                                             )  # boto3.client("sns")
        self.snsTopic = snsTopic

    def publish(self, taxi: Taxi):
        self.client.publish(TopicArn=self.snsTopic, Message=json.dumps(taxi))


class TaxiLocationContext:
    def __init__(self, taxi: Taxi, location_generator: RandomLocationGenerator, taxi_status: Taxi_Status):
        self.taxi = taxi
        self.location_generator = location_generator
        self.taxi_status = taxi_status

    def get_location_generator(self):
        return self.location_generator

    def get_taxi(self):
        return self.taxi


    # sleep for 1 minute
