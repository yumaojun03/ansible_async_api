import tornado
import tornado.template
import os
from tornado.options import define, options

# add need module to PYTHONPATH
import environment


# Make filepaths relative to settings.
path = lambda root, *a: os.path.join(root, *a)
ROOT = os.path.dirname(os.path.abspath(__file__))

define("port", default=8888, help="run on the given port", type=int)
define("config", default=None, help="tornado config file")
define("debug", default=True, help="debug mode")
tornado.options.parse_command_line()

settings = {}
settings['xsrf_cookies'] = False

# See PEP 391 and logconfig for formatting help.  Each section of LOGGERS
# will get merged into the corresponding section of log_settings.py.
# Handlers and log levels are set up automatically based on LOG_LEVEL and DEBUG
# unless you set them here.  Messages will not propagate through a logger
# unless propagate: True is set.
from logconfig.logconfig import init_logging
init_logging()

if options.config:
    tornado.options.parse_config_file(options.config)




