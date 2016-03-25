# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from libs.utils import get_md5
from tornado.options import options
import ansible
import json
import tornado.web
import logging
import datetime
import time
logger = logging.getLogger('ansible_async_api.' + __name__)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class CommandHandler(tornado.web.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        _type = data['type']
        cmd = data['cmd']
        host = data['host']
        sign = data['sign']
        isudo = data['sudo']
        cmdinfo = cmd.split(" ", 1)
        hotkey = _type+host+options.key
        result = get_md5(hotkey)

        logger.info("hot key: %s" % hotkey)
        logger.info("result: %s" % result)

        if sign != result:
            self.write("Sign is Error")
        else:
            if "," in host:
               inventory = host.split(",")
               for host in inventory:
                   runner = ansible.runner.Runner(
                     module_name=_type,
                     module_args=cmd,
                     pattern=host,
                     sudo = isudo,
                     forks=ANSIBLE_FORKS
                   )
                   result = runner.run()
                   now = datetime.datetime.now()
                   true = 'True'
                   result['time'] = now.strftime(TIME_FORMAT)
                   result['type'] = 'ad-hoc'
                   result['sudo'] = isudo
                   result['cmd'] = cmd
                   result['inventory'] = host
                   self.write(result)

                   uri = ConnMongoDB()
                   client = MongoClient(uri, safe=False)
                   db = client.ansible_log
                   db.ad_hoc.insert(result)
            else:
               runner = ansible.runner.Runner(
                     module_name=_type,
                     module_args=cmd,
                     pattern=host,
                     sudo = isudo,
                     forks=ANSIBLE_FORKS
               )
               result = runner.run()
               now = datetime.datetime.now()
               true = 'True'
               result['time'] = now.strftime(TIME_FORMAT)
               result['type'] = 'ad-hoc'
               result['sudo'] = isudo
               result['cmd'] = cmd
               result['inventory'] = inventory
               self.write(result)

               uri = ConnMongoDB()
               client = MongoClient(uri, safe=False)
               db = client.ansible_log
               db.ad_hoc.insert(result)


class AsyncTaskHandler(tornado.web.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)

        type = data['type']
        cmd = data['cmd']
        inventory = data['host']
        sign = data['sign']
        isudo = data['sudo']
        cmdinfo = cmd.split(" ", 1)
        print type, inventory, options.key
        hotkey = type + inventory + options.key
        print hotkey
        result = get_md5(hotkey)
        print result

        now = datetime.datetime.now()

        taskinfo = {}
        taskinfo['mode'] = type
        taskinfo['cmd'] = cmd
        taskinfo['inventory'] = inventory
        taskinfo['type'] = 'async ad-hoc'
        taskinfo['start'] = now.strftime(TIME_FORMAT)
        taskinfo['sudo'] = isudo

        uri = ConnMongoDB()
        client = MongoClient(uri, safe=False)
        db = client.ansible_log
        id=db.ansible_task.insert(taskinfo)
        mongoid={"_id":ObjectId(id)}
        print id

        if sign != result:
            self.write("Sign is Error")
        else:
                runner = ansible.runner.Runner(
                    module_name=type,
                    module_args=cmd,
                    pattern=inventory,
                    sudo = isudo,
                    forks=ANSIBLE_FORKS
                )
                _, res = runner.run_async(time_limit = WORKER_TIMEOUT)
                now = time.time()
                while True:
                  if res.completed or time.time() - now > WORKER_TIMEOUT:
                      break
                  results = res.poll()
                  results = results.get('contacted')
                  if results:
                     for result in results.items():
                       jobinfo = {}
                       data = result[1]
                       print data
                       inventory = result[0]
                       jobinfo['inventory']=inventory
                       jobinfo['job_id']=data['ansible_job_id']
                       jobinfo['cmd']=data['cmd']
                       jobinfo['task_id']=id
                       uri = ConnMongoDB()
                       client = MongoClient(uri, safe=False)
                       db = client.ansible_log
                       id2 = db.ansible_job.insert(jobinfo)
                       mongoid2 = {"_id":ObjectId(id2)}

                       if data['rc'] == 0 :
                         thisinfo2 = db.ansible_job.find_one(mongoid2)
                         thisinfo2['rc']=data['rc']
                         thisinfo2['stdout']=data['stdout']
                         thisinfo2['stderr']=data['stderr']
                         db.ansible_job.save(thisinfo2)
                         thisinfo = db.ansible_task.find_one(mongoid)
                         thisinfo['end'] = data['end']
                         thisinfo['rc'] = data['rc']
                         db.ansible_task.save(thisinfo)

                       elif data['rc'] == 1 :
                         thisinfo2 = db.ansible_job.find_one(mongoid2)
                         thisinfo2['rc']=data['rc']
                         thisinfo2['stderr']=data['stderr']
                         db.ansible_job.save(thisinfo2)
                         thisinfo = db.ansible_task.find_one(mongoid)
                         thisinfo['rc'] = data['rc']
                         db.ansible_task.save(thisinfo)

                       else:
                         thisinfo2 = db.ansible_job.find_one(mongoid2)
                         thisinfo2['rc']=data['rc']
                         thisinfo2['stderr']=data['msg']
                         db.ansible_job.save(thisinfo2)
                         thisinfo = db.ansible_task.find_one(mongoid)
                         thisinfo['rc'] = data['rc']
                         db.ansible_task.save(thisinfo)
                time.sleep(2)