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
import time
import uuid

import jwt


class JwtHelper:
    """ Class to create and parse JWT."""

    # Secret to use!
    __secret: str

    def __init__(self, secret: str):
        self.__secret = secret

    def create_jwt(self, identity: str, minutes: int) -> str:
        assert isinstance(minutes, int)
        assert minutes > 0
        assert minutes < 6
        assert isinstance(identity, str)
        assert identity.strip() != ""
        payload = dict()
        payload['nonce'] = str(uuid.uuid4())
        payload['expiry'] = int(time.time()) + (minutes * 60)
        payload['identity'] = identity
        return jwt.encode(payload=payload, key=self.__secret, algorithm="HS256")

    def validate_jwt(self, identity: str, token: str) -> bool:
        try:
            payload: dict = jwt.decode(jwt=token, key=self.__secret, algorithms="HS256")
            expiry = int(payload['expiry'])
            return expiry > int(time.time()) and identity == payload['identity']
        except Exception as ex:
            print(ex)
            return False
