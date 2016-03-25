from handlers.ansible_async import MainHandler, AsyncTaskHandler, CommandHandler

url_patterns = [
    (r"/", MainHandler),
    (r"/asynctask", AsyncTaskHandler),
    (r"/command", CommandHandler),
]