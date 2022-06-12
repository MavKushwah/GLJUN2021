#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Restricted Software.
# Copyright (c) 2022 My Great Learning.
# All Rights Reserved.
#
# @author Shanger Sivaramachandran
# @since 2022.05
import json

from bson import ObjectId
from core.mongodbconnection import MongoDBConnection

COL_TAXI = 'taxi_profile'
COL_USER = 'user_profile'
COL_RIDES = 'rides'
COL_LOC_HIST = 'taxi_location_history'


class DatabaseDriver:
    def __init__(self, mongo_uri: str, database_name: str):
        self.database_name = database_name
        self.cli = MongoDBConnection(mongo_uri, database_name)
        self.create_database_with_collections()

    # Create database if doesn't exist.
    def create_database_with_collections(self):
        with self.cli:
            db = self.cli.connection[self.database_name]
            db[COL_TAXI]
            db[COL_USER]
            db[COL_RIDES]
            self.create_index()

    # get taxi record by id
    def get_taxi(self, taxi_id: str) -> dict:
        with self.cli:
            db = self.cli.connection[self.database_name]
            return dict(db['taxi_profile'].find_one({'_id': ObjectId(taxi_id)}))

    # insert new taxi record here, return Id
    def create_taxi_record(self, taxi: dict) -> str:
        with self.cli:
            db = self.cli.connection[self.database_name]
            taxi_id = db[COL_TAXI].insert_one(taxi).inserted_id
            taxi_location_col = COL_LOC_HIST + '_' + str(taxi_id)
            db[taxi_location_col]
            taxi_location_document = {"updated_timestamp": taxi["updated_timestamp"],
                                      "location": taxi["location"],
                                      "taxi_on_duty": taxi["taxi_on_duty"],
                                      "active_taxi": taxi["active_taxi"]}
            db[taxi_location_col].insert_one(taxi_location_document)
            return taxi_id

    # update taxi record
    def update_taxi_record(self, taxi_id: str, patch: dict):
        with self.cli:
            db = self.cli.connection[self.database_name]
            return db[COL_TAXI].update_one({"_id": ObjectId(taxi_id)}, {"$set": patch})

    def find_nearby_taxi(self, location: dict, type: str, radius: float, limit: int) -> list:
        metersPerKiloMeter = 1000
        with self.cli:
            db = self.cli.connection[self.database_name]
            find_taxi_query = {
                'location': {
                    '$near':
                        {
                            '$geometry': location, '$maxDistance': radius * metersPerKiloMeter
                        }
                },
                "type": type,
                "taxi_on_duty": False,
                "active_taxi": True,
            }
            if type == "ALL":
                find_taxi_query.pop("type")

            taxi_list = db[COL_TAXI].find(find_taxi_query)
            print(json.dumps(find_taxi_query))

            nearByTaxiList = []
            print(f"Near by taxi : {taxi_list}")
            for taxi in range(limit):
                for taxi in taxi_list:
                    nearByTaxiList.append(taxi)
            return nearByTaxiList

    # return list of all taxi records
    def list_all_taxis(self) -> list:
        with self.cli:
            db = self.cli.connection[self.database_name]
            return list(db[COL_TAXI].find())

    # return user record by id.
    def get_user(self, user_id: str) -> dict:
        with self.cli:
            db = self.cli.connection[self.database_name]
            return dict(db[COL_USER].find_one({'_id': ObjectId(user_id)}))

    # insert new user record here, return Id
    def create_user_record(self, user: dict) -> str:
        with self.cli:
            db = self.cli.connection[self.database_name]
            return db[COL_USER].insert_one(user).inserted_id

    # Create new ride for the user.
    def create_new_ride(self, ride: dict) -> str:
        with self.cli:
            db = self.cli.connection[self.database_name]
            return db[COL_RIDES].insert_one(ride).inserted_id

    # Update Ride status and end time of the ride.
    def update_ride_status(self, ride_id, ride_status: str, ride_completion_time):
        with self.cli:
            db = self.cli.connection[self.database_name]
            return db[COL_RIDES].find_and_modify({"_id": ObjectId(ride_id)}, {"$set": {"ride_status": ride_status,
                                                                        "completion_time": ride_completion_time}})

    def update_ride(self, ride_id, query: dict, update_by: dict):
        with self.cli:
            db = self.cli.connection[self.database_name]
            filter_query = dict(query)
            filter_query["_id"] = ObjectId(ride_id)
            return db[COL_RIDES].find_one_and_update(filter_query, {"$set": update_by})

    # update the latest location of the taxi.
    def update_latest_taxi_location(self, taxi_id, patch: dict):
        with self.cli:
            db = self.cli.connection[self.database_name]
            db[COL_TAXI].update_one({"_id": taxi_id}, {"$set": {"updated_timestamp": patch["updated_timestamp"],
                                                                "location": patch["location"],
                                                                "taxi_on_duty": patch["taxi_on_duty"],
                                                                "active_taxi": patch["active_taxi"]}})
            return db[COL_LOC_HIST + '_' + taxi_id].insert_one(patch)

    # Drop all collections.
    def drop_all_collections(self):
        with self.cli:
            db = self.cli.connection[self.database_name]
            collection_list = db.list_collection_names()
            for collection in collection_list:
                collection.drop()

    def create_index(self):
        with self.cli:
            db = self.cli.connection[self.database_name]
            db[COL_TAXI].create_index([('location', '2dsphere')])
            db[COL_RIDES].create_index([('location', '2dsphere')])

    # return ride record by id.
    def get_ride(self, ride_id: str) -> dict:
        with self.cli:
            db = self.cli.connection[self.database_name]
            return dict(db[COL_RIDES].find_one({'_id': ObjectId(ride_id)}))
