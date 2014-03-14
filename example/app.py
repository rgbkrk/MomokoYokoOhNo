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

from sqlalchemy.orm import sessionmaker

import alchemy
from alchemy import User

class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

    @property
    def Session(self):
        return self.application.Session


class TutorialHandler(BaseHandler):
    @asynchronous
    def get(self):
        self.db.execute('SELECT 1;', callback=self._done)

    def _done(self, cursor, error):
        self.write('Results: %r' % (cursor.fetchall(),))
        self.finish()

class TutorialHandler2(BaseHandler):
    @gen.coroutine
    def get(self):
        try:
            cursor = yield momoko.Op(self.db.execute, 'SELECT 1;')
        except (psycopg2.Warning, psycopg2.Error) as error:
            self.write(str(error))
        else:
            self.write('Results: %r' % (cursor.fetchall(),))

        self.finish()

class TutorialHandler3(BaseHandler):
    @gen.coroutine
    def get(self):
        self.db.execute('SELECT 1;', callback=(yield gen.Callback('q1')))
        self.db.execute('SELECT 2;', callback=(yield gen.Callback('q2')))
        self.db.execute('SELECT 3;', callback=(yield gen.Callback('q3')))

        try:
            cursor1 = yield momoko.WaitOp('q1')
            cursor2 = yield momoko.WaitOp('q2')
            cursor3 = yield momoko.WaitOp('q3')
        except (psycopg2.Warning, psycopg2.Error) as error:
            self.write(str(error))
        else:
            self.write('Q1: %r<br>' % (cursor1.fetchall(),))
            self.write('Q2: %r<br>' % (cursor2.fetchall(),))
            self.write('Q3: %r<br>' % (cursor3.fetchall(),))

        self.finish()

class TutorialHandler4(BaseHandler):
    @gen.coroutine
    def get(self):
        chunk = 1000
        try:
            connection = yield momoko.Op(self.db.getconn)
            with self.db.manage(connection):
                yield momoko.Op(connection.execute, "BEGIN")
                yield momoko.Op(connection.execute, "DECLARE all_ints CURSOR FOR SELECT * FROM unit_test_int_table")
                rows = True
                while rows:
                    cursor = yield momoko.Op(connection.execute, "FETCH %s FROM all_ints", (chunk,))
                    rows = cursor.fetchall()
                    # Do something with results...
                yield momoko.Op(connection.execute, "CLOSE all_ints")
                yield momoko.Op(connection.execute, "COMMIT")
        except Exception as error:
            self.write(str(error))

class SillyHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        try:
            import random
            myid = unicode(random.random())
            session = self.Session()

            user = User(name=u'dav{}'.format(myid),
                        fullname='dave rino', twitter='davarino')
            print(user)
            self.write("<p>")
            self.write(myid + "\n")
            self.write("</p>")

            session.add(user)
            session.commit()

            cursor = yield momoko.Op(self.db.execute, 'SELECT * from users;')
        except (psycopg2.Warning, psycopg2.Error) as error:
            self.write(str(error))
        else:
            self.write('Results: %r' % (cursor.fetchall(),))


class UserQuery(BaseHandler):
    @gen.coroutine
    def get(self):
        try:
            session = self.Session()
            results = session.query(User).filter(User.name.contains('36')).all()
            self.write(unicode(results))
        except Exception as e:
            self.write(str(e))
        else:
            self.write("<marquee>Wee Marquee</marquee>")

if __name__ == '__main__':
    define("dbname", default="postgres", help="Database name")
    define("dbuser", default="postgres", help="Postgres user")
    define("dbpass")
    define("dbhost", default="localhost")
    define("dbport", default="5432")

    parse_command_line()

    application = Application([
        (r'/', TutorialHandler),
        (r'/2', TutorialHandler2),
        (r'/3', TutorialHandler3),
        (r'/silly', SillyHandler),
        (r'/users', UserQuery)
    ], debug=True)


    # Set up Momoko
    dsn_template = ('dbname={} user={} password={}'
                    'host={} port={}')

    dsn = dsn_template.format(options.dbname, options.dbuser, options.dbpass,
                              options.dbhost, options.dbport)

    application.db = momoko.Pool(
        dsn=dsn,
        size=1
    )

    # Set up SQLAlchemy
    engine = alchemy.create_engine_from_params(options.dbname, options.dbuser,
                                               options.dbpass, options.dbhost,
                                               options.dbport)

    application.engine = engine
    application.Session = sessionmaker(bind=engine)

    http_server = HTTPServer(application)
    http_server.listen(8888, 'localhost')
    IOLoop.instance().start()
