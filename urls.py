from handlers.ansible_async import MainHandler, CommandHandler

url_patterns = [
    (r"/", MainHandler),
    (r"/command", CommandHandler),
]