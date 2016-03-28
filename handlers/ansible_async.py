# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import tcelery
import json

import logging
from tornado import gen
from tornado.web import HTTPError
from tornado.web import RequestHandler, asynchronous
from libs import tasks

tcelery.setup_nonblocking_producer()
logger = logging.getLogger('tornado.app')


class MainHandler(RequestHandler):
    def get(self):
        self.write("Hello, world")


class CommandHandler(RequestHandler):
    @asynchronous
    @gen.coroutine
    def post(self):
        try:
            data = json.loads(self.request.body)
        except ValueError as e:
            raise HTTPError(400, e.message)
        logger.debug("input data: %s" % data)
        response = yield gen.Task(tasks.exec_command.apply_async, args=[data.get("resource"), data.get("command")])
        self.write(str(response.result))
        self.finish()


class AdHocHandler(RequestHandler):
    @asynchronous
    @gen.coroutine
    def post(self):
        try:
            data = json.loads(self.request.body)
        except ValueError as e:
            raise HTTPError(400, reason=e.message)
        logger.debug("input data: %s" % data)
        resource, module_name, module_arg = data.get("resource"), data.get("module_name"), data.get("module_arg")
        if not(resource and module_name and module_arg):
            raise HTTPError(400, reason="resource and module_name and module_arg are required.")

        response = yield gen.Task(tasks.ad_hoc.apply_async, args=[resource, module_name, module_arg])
        self.write(str(response.result))
        self.finish()

