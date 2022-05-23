#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Restricted Software.
# Copyright (c) 2022 My Great Learning.
# All Rights Reserved.
#
# @author Shanger Sivaramachandran
# @since 2022.05
#
import os

import pymongo
import pymongo_inmemory
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

COL_TAXI = 'taxi_profile'
COL_USER = 'user_profile'
COL_RIDES = 'rides'
COL_LOC_HIST = 'taxi_location_history'
COL_REQ_HIST = 'taxi_request_history'


class DatabaseDriver:
    # Mongo Uri to connect to Database;
    # The concern to generate the right template for Mongo Uri is a util to be shared between all components.
    client: pymongo.MongoClient
    # database_name
    database_name = str
    # Database Objects
    __database: Database

    def __init__(self, database_name: str, mongo_uri: str):
        if os.environ.get('mode') == 'LOCAL':
            self.client = pymongo.MongoClient("mongodb://127.0.0.1", 27017)
        else:
            self.client = pymongo.MongoClient(mongo_uri)
        self.database_name = database_name
        self.__create_database()
        self.__create_collections()

    def __create_database(self):
        """ Create database if it doesn't exist. """
        dblist = self.client.list_database_names()
        if self.database_name in dblist:
            print(f"Database {self.database_name} exists")
        else:
            print(f"Database {self.database_name} will be created")
        self.__database = self.client[self.database_name]

    def __create_collections(self):
        """ Create collections if collections doesn't exist."""

        existing_collections = self.__database.list_collection_names()
        for col_name in self.__get_all_collections():
            if col_name in existing_collections:
                print(f"collection {col_name} exists")
            else:
                print(f"collection {col_name} will be created")
                # Create indexes here!
                collection: Collection = self.__database[COL_RIDES]
                collection.create_index('taxi_id')
                collection.create_index('user_id')
                collection.create_index('status')

    @staticmethod
    def __get_all_collections() -> list:
        return [COL_TAXI, COL_USER, COL_RIDES, COL_LOC_HIST, COL_REQ_HIST]

    #
    # GET BY ID METHODS START HERE
    def get_by_id(self, col_name: str, record_id: str) -> dict:
        col: Collection = self.__database[col_name]
        return dict(col.find_one({'_id': ObjectId(record_id)}))

    def get_taxi(self, taxi_id: str) -> dict:
        return self.get_by_id(COL_TAXI, taxi_id)

    def get_user(self, user_id: str) -> dict:
        return self.get_by_id(COL_USER, record_id=user_id)

    def get_ride(self, ride_id: str) -> dict:
        return self.get_by_id(COL_RIDES, record_id=ride_id)

    #
    # Update Method Starts from Here
    def patch_by_query(self, col_name: str, query: dict, patch: dict) -> int:
        col: Collection = self.__database[col_name]
        return col.update_one(filter=query, update={"$set" : patch}).modified_count

    def patch_by_id(self, col_name: str, record_id: str, patch: dict) -> bool:
        return self.patch_by_query(col_name=col_name, query={'_id': ObjectId(record_id)}, patch=patch) == 1

    def patch_taxi(self, taxi_id: str, patch: dict) -> bool:
        return self.patch_by_id(col_name=COL_TAXI, record_id=taxi_id, patch=patch)

    def patch_user(self, user_id: str, patch: dict) -> bool:
        return self.patch_by_id(col_name=COL_USER, record_id=user_id, patch=patch)

    def patch_ride(self, ride_id: str, patch: dict) -> bool:
        return self.patch_by_id(col_name=COL_RIDES, record_id=ride_id, patch=patch)

    #
    # Create a new record
    def create_new_record(self, col_name: str, record: dict) -> str:
        col: Collection = self.__database[col_name]
        return str(col.insert_one(document=record).inserted_id)

    def create_taxi_record(self, taxi: dict) -> str:
        return self.create_new_record(col_name=COL_TAXI, record=taxi)

    def create_user_record(self, user: dict) -> str:
        return self.create_new_record(col_name=COL_USER, record=user)

    def create_ride_record(self, ride: dict) -> str:
        return self.create_new_record(col_name=COL_RIDES, record=ride)

    # Run Query!
    def run_query(self, col_name: str, query: dict, limit: int = 0) -> list:
        col: Collection = self.__database[col_name]
        return list(col.find(filter=query, limit=limit))

    # return list of all taxi records
    def list_all_record(self, col_name: str) -> list:
        taxi_profile: Collection = self.__database[col_name]
        return list(taxi_profile.find())

    def clear_all_data(self):
        for c_name in self.__get_all_collections():
            col: Collection = self.__database[c_name]
            col.drop()
