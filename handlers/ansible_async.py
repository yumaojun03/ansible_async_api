# -*- coding:utf-8 -*-
from __future__ import unicode_literals


import ansible
import json
import tornado.web
import logging
from tornado.web import HTTPError

logger = logging.getLogger('tornado.app')

from libs.my_ansible_api import Command


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class CommandHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            data = json.loads(self.request.body)
        except ValueError as e:
            raise HTTPError(400, e.message)
        logger.debug("input data: %s" % data)

        resource = data.get("resource")
        command = data.get("command")
        if not (resource and command):
            raise HTTPError(400)
        cmd = Command(resource)
        result = cmd.run(command)
        logger.debug("command result: %s" % result.result_deal)

        self.write(result.result_deal)

