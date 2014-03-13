#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer

import tornado.options
from tornado.options import define, options

from tornado.options import parse_command_line
from tornado.web import *

import psycopg2
import momoko


class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db


class TutorialHandler(BaseHandler):
    @asynchronous
    def get(self):
        self.db.execute('SELECT 1;', callback=self._done)

    def _done(self, cursor, error):
        self.write('Results: %r' % (cursor.fetchall(),))
        self.finish()


if __name__ == '__main__':
    define("dbname", default="postgres", help="Database name")
    define("dbuser", default="postgres", help="Postgres user")
    define("dbpass")
    define("dbhost", default="localhost")
    define("dbport", default="5432")

    parse_command_line()

    application = Application([
        (r'/', TutorialHandler)
    ], debug=True)

    dsn_template = ('dbname={} user={} password={}'
                    'host={} port={}')

    dsn = dsn_template.format(options.dbname, options.dbuser, options.dbpass,
                              options.dbhost, options.dbport)

    application.db = momoko.Pool(
        dsn=dsn,
        size=1
    )

    http_server = HTTPServer(application)
    http_server.listen(8888, 'localhost')
    IOLoop.instance().start()
