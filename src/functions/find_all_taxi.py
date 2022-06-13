#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Restricted Software.
# Copyright (c) 2022 My Great Learning.
# All Rights Reserved.
#
# @author Nilotpal Sarkar
# @since 2022.06
#

from .utils import *
from core import DatabaseDriver


def handler(event, context):
    db_driver: DatabaseDriver = get_db_driver()
    taxis: list = db_driver.list_all_taxis()
    if taxis is not None:
        return ok_response(taxis)
    else:
        return ok_response({})
