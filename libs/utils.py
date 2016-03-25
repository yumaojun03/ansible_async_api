# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from settings import mongoinfo
import hashlib
from pymongo import MongoClient


def get_md5(s):
    """
    hash　一段字符串

    Args:
        s: <string> 一段字符串
    Returns:
        digest: <str> hash过后的digest
    """
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


def conn_mongodb():
    """
    返回一个mongodb的uri，用于链接mongodb
    """
    dbhost = mongoinfo['host']
    dbport = mongoinfo['port']
    dbuser = mongoinfo['user']
    dbpwd = mongoinfo['password']
    dbname = mongoinfo['dbname']
    uri = 'mongodb://%s:%s@%s:%s/%s' % (dbuser, dbpwd, dbhost, dbport, dbname)
    return MongoClient(uri, safe=False)
