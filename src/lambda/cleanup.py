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
from utils import *


def handler(event, context):
    # purge
    print('purging all data in database')
    get_db_driver().clear_all_data()
    return respond(200, "some people just want the world to burn! data has been nuked.", {})
