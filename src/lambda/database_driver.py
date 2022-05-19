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
from pymongo import MongoClient


class DatabaseDriver:
    #  connection url
    db_url: str
    # Database name
    db_name: str
    # Mongo client
    client: MongoClient

    def __init__(self, db_url: str, db_name: str):
        self.db_url = db_url
        self.db_name = db_name
        self.client = MongoClient(db_url)

    def get_taxi(self, taxi_id: str) -> dict:
        db = self.client[self.db_name]
        # @TODO get taxi record by id
        return dict({"taxi_id": taxi_id, "secret": taxi_id, "uuid": taxi_id})

    def create_taxi_record(self, taxi: dict) -> str:
        db = self.client[self.db_name]
        # @TODO insert new taxi record here, return Id
        return ""

    def update_taxi_record(self, taxi_id: str, patch: dict):
        db = self.client[self.db_name]
        # @TODO patch the records
        return True

    def find_nearby_taxi(self, location: list, radius: float, limit: int) -> list:
        db = self.client[self.db_name]
        # @TODO return list of all taxi_ids
        return list()

    def list_all_taxis(self) -> list:
        db = self.client[self.db_name]
        # @TODO return list of all taxi records
        return list()

    def get_user(self, user_id: str) -> dict:
        db = self.client[self.db_name]
        # @TODO get user record by id
        return dict()

    def create_user_record(self, user: dict) -> str:
        db = self.client[self.db_name]
        # @TODO insert new user record here, return Id
        return ""

    def clear_all_data(self) -> str:
        db = self.client[self.db_name]
        # @TODO purge all collections so that database becomes empty
        return ""
