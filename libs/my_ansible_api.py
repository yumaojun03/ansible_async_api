# -*- coding: utf-8 -*-
"""
Purpose: This module is for custom ansible api for tornado.
Author: Yu Maojun
Date: 2016-03-20
Version: 0.0.1
"""


from __future__ import print_function, unicode_literals
from ansible.inventory import Inventory
from ansible.inventory.group import Group
from ansible.inventory.host import Host
from ansible.runner import Runner
from ansible.playbook import PlayBook
from ansible import callbacks, utils

import os
import ansible.constants as C

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYBOOK_DIR = os.path.join(ROOT_DIR, 'ansible_playbooks')


def config_ansible():
    C.HOST_KEY_CHECKING = False
    C.DEFAULT_MODULE_PATH = os.path.join(ROOT_DIR, 'extra_ansible_modules')


class AnsibleError(StandardError):
    """
    the base AnsibleError which contains all error message.

    Attributes:
        message: <str> the main error message
        kwargs: <dict> the other message data
    """
    def __init__(self, message='', **kwargs):
        super(AnsibleError, self).__init__(message)
        self.message = message
        for key, value in kwargs.items():
            setattr(self, key, value)


class CommandError(AnsibleError):
    """
    the ansible command execute error.
    """
    def __init__(self, message=''):
        super(CommandError, self).__init__(message)


class ResourceBase(object):
    """
    gen_inventory methods.

    Attributes:
        resource: the inventory's resource. format:
                    {
                        "group1": {
                            "hosts": [{"hostname": "10.10.10.10", "port": "22", "username": "test", "password": "mypass"}, ...],
                            "vars": {"var1": value1, "var2": value2, ...}
                        }
                    }
                  if your pass a list, the list will add the default group(default_group)
                    [{"hostname": "10.10.10.10", "port": "22", "username": "test", "password": "mypass"}, ...]
        inventory: ansible inventory object use gen_inventory to generate.
    Methods:
        gen_inventory: generate a ansible inventory object.
    """

    def __init__(self, resource):
        self.inventory = Inventory(host_list=[])
        self.resource = resource
        self.gen_inventory()

    @staticmethod
    def add_group_vars(group, group_vars=None):
        """
        if group_vars exists then, add group variable to group

        Args:
            group: <ansible group object> ansible group object
            group_vars: <dict> group variables
        """
        assert isinstance(group, Group), "the group must be an ansible group object."

        if group_vars:
            for key, value in group_vars.iteritems():
                group.set_variable(key, value)

    @staticmethod
    def gen_hosts(hosts=None):
        """
        if host_vars exists then, generate hosts

        Args:
             hosts: <list> [<host variable dict>, <host variable dict>, ...]
        Returns:
             host_objs: <list> [<host object>, <host object>, ...]
        """
        assert isinstance(hosts, list), "the hosts must be a list"
        host_objs = []
        if hosts:
            for host in hosts:
                hostname = host.get("hostname")
                hostip = host.get('ip', hostname)
                hostport = host.get("port")
                username = host.get("username")
                password = host.get("password")
                ssh_key = host.get("ssh_key")

                my_host = Host(name=hostname, port=hostport)
                my_host.set_variable('ansible_ssh_host', hostip)
                my_host.set_variable('ansible_ssh_port', hostport)
                my_host.set_variable('ansible_ssh_user', username)

                if password:
                    my_host.set_variable('ansible_ssh_pass', password)
                if ssh_key:
                    my_host.set_variable('ansible_ssh_private_key_file', ssh_key)

                # set other variables
                for key, value in host.iteritems():
                    if key not in ["hostname", "port", "username", "password", "ip", "ssh_key"]:
                        my_host.set_variable(key, value)
                host_objs.append(my_host)
        return host_objs

    def my_add_group(self, hosts_vars, group_name, group_vars=None):
        """
        add hosts to group. use to generate a inventory.

        Args:
            hosts_vars: the hosts variables
            group_name: group name
            group_vars: group variables
        """
        my_group = Group(name=group_name)
        self.add_group_vars(my_group, group_vars)
        for host in self.gen_hosts(hosts_vars):
            my_group.add_host(host)
        self.inventory.add_group(my_group)

    def gen_inventory(self):
        """
        add hosts to an inventory.
        """
        if isinstance(self.resource, list):
            self.my_add_group(self.resource, 'default_group')
        elif isinstance(self.resource, dict):
            for group_name, hosts_vars in self.resource.iteritems():
                self.my_add_group(hosts_vars.get("hosts"), group_name, hosts_vars.get("vars"))


class Ad_Hoc(ResourceBase):
    """
    execute ansible ad-hoc mode in inventory.

    Args:
        resource:　the inventory resource, the resource format see MyRunner on top of this module
        command: which command your want to run in this resource
    Attributes:
        results_raw: the raw data returned after ansible run.
    """
    def __init__(self, resource):
        super(Ad_Hoc, self).__init__(resource)
        self.results_raw = {}

    def run(self, module_arg, module_name="shell", timeout=10, forks=10, pattern='*'):
        """
        run command from andible ad-hoc.

        Args:
            module_arg: ansible module argument
            module_name: which module want to use, default use shell
            timeout: set runner api
            forks: see runner api
            pattern: set runner api
        """
        hoc = Runner(module_name=module_name,
                     module_args=module_arg,
                     timeout=timeout,
                     inventory=self.inventory,
                     pattern=pattern,
                     forks=forks,
                     )
        self.results_raw = hoc.run()
        return AnsibleResult(self.results_raw)


class AnsibleResult(object):
    """
    container ansible return result.

    Attributes:
        result_raw: ansible return raw data
    """
    def __init__(self, raw_data):
        self.result_raw = raw_data

    @property
    def dark(self):
        """
        return the failed dark message.

        Returns:
            failed: <dict> eg:{'failed': {'localhost': ''}}
        """
        failed = {}
        dark = self.result_raw.get("dark")
        if dark:
            for host, info in dark.items():
                failed[host] = info.get('msg')
        return failed

    @property
    def contacted(self):
        """
        return the contacted message.

        Returns:
            contacted: <dict> {'failed': {'host1': ''}, 'ok': {'host2': ''}}
        """
        result = {'failed': {}, 'ok': {}}
        contacted = self.result_raw.get("contacted")
        if contacted:
            for host, info in contacted.items():
                if info.get('invocation').get('module_name') in ['raw', 'shell', 'command', 'script']:
                    if info.get('rc') == 0:
                        result['ok'][host] = info.get('stdout') + info.get('stderr')
                    else:
                        result['failed'][host] = info.get('stdout') + info.get('stderr')
                else:
                    if info.get('failed'):
                        result['failed'][host] = info.get('msg')
                    else:
                        result['ok'][host] = info.get('changed')
        return result

    @property
    def result_deal(self):
        """
        deal the ansible return result.

        Returns:
            results: <dict> eg: {'failed': {'host1': ''}, 'ok': {'host2': ''}}
        """
        results = {'failed': {}, 'ok': {}}
        if self.dark:
            results['failed'].update(**self.dark)
        if self.contacted:
            results['failed'].update(**self.contacted['failed'])
            results['ok'].update(**self.contacted['ok'])
        return results

    def __unicode__(self):
        return "%s" % self.result_raw

    def __str__(self):
        return self.__unicode__()


class MyPlaybook(ResourceBase):
    """
    this is my playbook object for execute playbook.

    Attributes:
        resource: resource dict ,see ResourceBase class
        playbook_path: relational playbook path, the default playbook directory is: <PLAYBOOK_DIR>
    """
    def __init__(self, resource, playbook_path):
        super(MyPlaybook, self).__init__(resource)
        self.results_raw = None
        self.playbook_path = playbook_path

    def run(self, extra_vars=None):
        """
        run ansible playbook, only surport relational path.

        Args:
            extra_vars: playbook extra variables.
        """
        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
        playbook_path = os.path.join(PLAYBOOK_DIR, self.playbook_path)

        pb = PlayBook(
            playbook=playbook_path,
            stats=stats,
            callbacks=playbook_cb,
            runner_callbacks=runner_cb,
            inventory=self.inventory,
            extra_vars=extra_vars,
            check=False)

        self.results_raw = pb.run()
        return self.results_raw


if __name__ == "__main__":
    resource = [{"hostname": "192.168.10.148", "port": "22", "username": "root", "password": "mypass"}]
    cmd = Ad_Hoc(resource)
    result = cmd.run('time')
    print(result.result_deal)
