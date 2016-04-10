# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import json

import logging
from tornado import gen
from tornado.web import HTTPError
from tornado.web import RequestHandler, asynchronous
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor


from libs.my_ansible_api import Ad_Hoc, MyPlaybook
from multiprocessing import cpu_count

logger = logging.getLogger('tornado.app')


class MainHandler(RequestHandler):
    def get(self):
        self.write("Hello, world")


class CommandHandler(RequestHandler):
    executor = ThreadPoolExecutor(cpu_count())

    @asynchronous
    @gen.coroutine
    def post(self):
        try:
            data = json.loads(self.request.body)
        except ValueError as e:
            raise HTTPError(400, e.message)
        logger.debug("input data: %s" % data)
        response = yield self.exec_command(data.get("resource"), data.get("command"))
        self.write(str(response))
        self.finish()

    @run_on_executor
    def exec_command(self, resource, command):
        """
        use ansible shell module to execute command on inventory.

        Args:
            resource: inventory resource, see Resource Class
            command: which command you want to execute
        Returns:
            AnsibleReuslt: AnsibleResult instance, contain the all ansible return information.
        """
        res = Ad_Hoc(resource)
        result = res.run(command, 'shell')
        return result.result_deal


class AdHocHandler(RequestHandler):
    executor = ThreadPoolExecutor(cpu_count())

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

        response = yield self.ad_hoc(resource, module_name, module_arg)
        self.write(str(response))
        self.finish()

    @run_on_executor
    def ad_hoc(self, resource, module_name, module_arg):
        """
        执行ansible hoc-ad

        Args:
            resource:  ditto
            module_name: ditto
            module_arg: ditto
        """
        res = Ad_Hoc(resource)
        result = res.run(module_arg, module_name)
        return result.result_deal


class PlaybookHandler(RequestHandler):
    executor = ThreadPoolExecutor(cpu_count())

    @asynchronous
    @gen.coroutine
    def post(self):
        try:
            data = json.loads(self.request.body)
        except ValueError as e:
            raise HTTPError(400, reason=e.message)
        logger.debug("input data: %s" % data)
        resource, playbook = data.get("resource"), data.get("playbook")
        if not(resource and playbook):
            raise HTTPError(400, reason="resource and playbook are required.")

        response = yield self.run(resource, playbook)
        self.write(str(response))
        self.finish()

    @run_on_executor
    def run(self, resource, playbook):
        """
        执行ansible playbook

        Args:
            resource:  ditto
            playbook: ditto
        """
        res = MyPlaybook(resource, playbook)
        result = res.run()
        return result

