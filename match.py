#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: anchen
# @Date:   2015-12-22 10:17:48
# @Last Modified by:   anchen
# @Last Modified time: 2015-12-23 01:21:36
import pymysql
from pymysql.cursors import DictCursor
import genprint
import database

def getcutprint(cutname):

    name, songhash, printhash = genprint.getsongprint(cutname)
    
    return printhash

def match(printhash):

    database.cur.execute("SELECT * FROM fingerprints;")

    match = []
    for i in database.cur:
        for j in printhash:
            if i[0] == j[0][-10:]:
                offset_diff = i[2] - j[1]
                match.append((offset_diff, i[1]))

    sid = getid(match)

    database.cur.execute("SELECT song_name FROM songs WHERE song_id = %d;" %(sid))
    songname = database.cur.fetchone()
    print(songname)

def getid(match):

    repeat = {}
    for i in match:
        repeat[i] = match.count(i)

    sid = 0
    most = 0
    for i in repeat:
        if repeat[i] > most:
            most = repeat[i]
            sid = i[1]

    return sid

printhash = getcutprint('test.mp3')
match(printhash)