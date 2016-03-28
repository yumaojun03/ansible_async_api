# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from my_ansible_api import Ad_Hoc
from celery import Celery
import os

celery = Celery('tasks', broker='amqp://')
celery.conf.CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'amqp')


@celery.task(name='task.exec_command')
def exec_command(resource, command):
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


@celery.task(name='task.ad_hoc')
def ad_hoc(resource, module_name, module_arg):
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


if __name__ == "__main__":
    celery.start()

