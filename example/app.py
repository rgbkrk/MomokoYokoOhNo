#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.options import parse_command_line
from tornado.web import *

import psycopg2
import momoko


class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db


class TutorialHandler(BaseHandler):
    def get(self):
        self.write('Some text here!')
        self.finish()


if __name__ == '__main__':
    parse_command_line()
    application = Application([
        (r'/', TutorialHandler)
    ], debug=True)

    application.db = momoko.Pool(
        dsn='dbname=your_db user=your_user password=very_secret_password '
            'host=localhost port=5432',
        size=1
    )

    http_server = HTTPServer(application)
    http_server.listen(8888, 'localhost')
    IOLoop.instance().start()

