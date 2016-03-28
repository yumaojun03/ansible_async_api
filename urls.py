from handlers.ansible_async import MainHandler, CommandHandler, AdHocHandler

url_patterns = [
    (r"/", MainHandler),
    (r"/command", CommandHandler),
    (r"/ad_hoc", AdHocHandler),
]