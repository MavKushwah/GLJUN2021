#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Restricted Software.
# Copyright (c) 2022 My Great Learning.
# All Rights Reserved.
#
# @author Shanger Sivaramachandran
# @since 2022.05
import mongodbconnection

COL_TAXI = 'taxi_profile'
COL_USER = 'user_profile'
COL_RIDES = 'rides'
COL_LOC_HIST = 'taxi_location_history'


class DatabaseDriver:
    def __init__(self, mongo_uri: str, database_name: str):
        self.database_name = database_name
        self.cli = mongodbconnection.MongoDBConnection(mongo_uri, database_name)
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
            return dict(db['taxi_profile'].find({taxi_id: taxi_id}))

    # insert new taxi record here, return Id
    def create_taxi_record(self, taxi: dict) -> str:
        with self.cli:
            db = self.cli.connection[self.database_name]
            taxi_location_col = COL_LOC_HIST + '_' + taxi['taxi_id']
            db[taxi_location_col]
            historic_location = self.Update_location_history(taxi['active_taxi'], taxi['location'], taxi['taxi_on_duty'], taxi['updated_timestamp'])
            db[taxi_location_col].insert_one(historic_location)
            return db[COL_TAXI].insert_one(taxi)

    # update taxi record
    def update_taxi_record(self, taxi_id: str, patch: dict):
        with self.cli:
            db = self.cli.connection[self.database_name]
            return db[COL_TAXI].update({"taxi_id": taxi_id}, {"$set": patch})

    def find_nearby_taxi(self, location: dict, taxi_type: str, radius: float, limit: int) -> list:
        metersPerKiloMeter = 1000
        with self.cli:
            db = self.cli.connection[self.database_name]
            taxi_list = db[COL_TAXI].find({
                'location': {
                    '$near':
                        {
                            '$geometry': location, '$maxDistance': radius * metersPerKiloMeter
                        }
                },
                "taxi_type": taxi_type,
                "taxi_on_duty": True,
                "active_taxi": False,
            })

            nearByTaxiList = []
            for taxi in range(limit - 1):
                for taxi in taxi_list:
                    nearByTaxiList.append(taxi['taxi_id'])
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
            return dict(db[COL_USER].find({user_id: user_id}))

    # insert new user record here, return Id
    def create_user_record(self, user: dict) -> str:
        with self.cli:
            db = self.cli.connection[self.database_name]
            return db[COL_USER].insert_one(user)

    # Create new ride for the user.
    def create_new_ride(self, ride: dict) -> str:
        with self.cli:
            db = self.cli.connection[self.database_name]
            return db[COL_RIDES].insert_one(ride)

    # Update Ride status and end time of the ride.
    def update_ride_status(self, ride_id, ride_status: str, ride_completion_time):
        with self.cli:
            db = self.cli.connection[self.database_name]
            return db[COL_RIDES].update({"ride_id": ride_id}, {"$set": {"ride_status": ride_status,
                                                                        "completion_time": ride_completion_time}})

    # update the latest location of the taxi.
    def update_latest_taxi_location(self, taxi_id, updated_timestamp, location, taxi_on_duty, active_taxi):
        with self.cli:
            db = self.cli.connection[self.database_name]
            db[COL_TAXI].update_one({"taxi_id": taxi_id}, {"$set": {str(updated_timestamp): updated_timestamp,
                                                                    "location": location,
                                                                    "taxi_on_duty": taxi_on_duty,
                                                                    "active_taxi": active_taxi}})
            historic_location = self.Update_location_history(active_taxi, location, taxi_on_duty, updated_timestamp)
            return db[COL_LOC_HIST + '_' + taxi_id].insert_one(historic_location)

    # to construct dictionary for location_history.
    def Update_location_history(self, active_taxi, location, taxi_on_duty, updated_timestamp):
        historic_location = {}
        historic_location['location'] = {}
        historic_location['location']['type'] = 'Point'
        historic_location['location']['coordinates'] = []
        historic_location['location']['coordinates'] = location
        historic_location['location']['time_stamp'] = updated_timestamp
        historic_location['location']['taxi_on_duty'] = taxi_on_duty
        historic_location['location']['active_taxi'] = active_taxi
        return historic_location

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
