import os, cherrypy, psycopg2
from psycopg2 import extras as pg_extras

import settings

""" Setup
"""
cherrypy.config.update(settings.CP_CONFIG)

""" Helper objects
"""
class DB:
    """ Simple DB wrapper
    """
    def __init__(self, dsn = None):
        self.dsn = ''
        self.connection = None
        self.cursor = None
        if dsn:
            self.connect(dsn)

    def connect(self, dsn):
        """ Connect to a DB and return a cursor
        """
        self.connection = psycopg2.connect(dsn)
        self.cursor = self.connection.cursor(cursor_factory=pg_extras.DictCursor)
        return self.cursor

    def disconnect(self):
        self.cursor.close()
        self.connection.close()

""" Views
"""
#@cherrypy.expose
@cherrypy.tools.json_out()
class Test:
    exposed = True
    def GET(self, test_id = None):
        """ Return JSON detail of a test
        """
        db = DB()
        cur = db.connect(settings.DSN)

        def multiple(self):
            """ Return JSON of tests in the DB
            """
            cur.execute("""SELECT
                                test_id, 
                                t.name, 
                                lastrun, 
                                schedule_id, 
                                s.name AS schedule_name, 
                                database_id,
                                d.name AS database_name
                                FROM pq_test t
                                LEFT JOIN pq_schedule s USING (schedule_id)
                                LEFT JOIN pq_database d USING (database_id)
                                ORDER BY lastrun;""")

            tests = []
            for test in cur.fetchall():
                t = {
                    'test_id':          test['test_id'],
                    'name':             test['name'],
                    'lastrun':          test['lastrun'],
                    'schedule_id':      test['schedule_id'],
                    'schedule_name':    test['schedule_name'],
                    'database_id':      test['database_id'],
                    'database_name':    test['database_name'],
                }
                tests.append(t)

            return tests

        def single(self):

            cur.execute("""SELECT
                                test_id, 
                                t.name, 
                                lastrun, 
                                schedule_id, 
                                database_id,
                                test_type_id,
                                sql,
                                python
                                FROM pq_test t
                                LEFT JOIN pq_schedule s USING (schedule_id)
                                LEFT JOIN pq_database d USING (database_id)
                                WHERE test_id = %s
                                ORDER BY lastrun;""", test_id)

            if cur.rowcount > 0:
                test = cur.fetchone()
                t = {
                    'test_id':          test['test_id'],
                    'name':             test['name'],
                    'lastrun':          test['lastrun'],
                    'schedule_id':      test['schedule_id'],
                    'database_id':      test['database_id'],
                    'test_type_id':     test['test_type_id'],
                    'sql':              test['sql'],
                    'python':           test['python']
                }
            else:
                raise cherrypy.HTTPError(404) 

            db.disconnect()
            return t

        if test_id:
            return single(self)
        else:
            return multiple(self)
            
    def POST(
        self, 
        test_id, 
        name = None, 
        schedule_id = None, 
        database_id = None, 
        test_type_id = None, 
        sql = None, 
        python = None):
        """ Insert/update a test
        """

        # sanity checks
        print type(test_id)

        return { 
            'result': 'failure',
            'message': 'Not yet done'
        }

@cherrypy.tools.json_out()
class Database:
    exposed = True
    def GET(self):
        """ Return JSON of known databases
        """
        db = DB()
        cur = db.connect(settings.DSN)
        cur.execute("SELECT database_id, name, username, port, hostname, active FROM pq_database ORDER BY name, hostname;")

        dbs = []
        for dbase in cur.fetchall():
            d = {
                'database_id':  dbase['database_id'],
                'name':         dbase['name'],
                'username':     dbase['username'],
                'port':         dbase['port'],
                'hostname':     dbase['hostname'],
                'active':       dbase['active'],
            }
            dbs.append(d)

        db.disconnect()

        return dbs

@cherrypy.tools.json_out()
class User:
    exposed = True
    def GET(self):
        """ Return JSON of users
        """
        db = DB()
        cur = db.connect(settings.DSN)
        cur.execute("SELECT user_id, username, email FROM pq_user ORDER BY username;")

        users = []
        for user in cur.fetchall():
            u = {
                'user_id':      user['user_id'],
                'username':     user['username'],
                'email':        user['email']
            }
            users.append(u)

        db.disconnect()

        return users

@cherrypy.tools.json_out()
class TestType:
    exposed = True
    def GET(self):
        """ Return JSON of test types
        """
        db = DB()
        cur = db.connect(settings.DSN)
        cur.execute("SELECT test_type_id, name FROM pq_test_type ORDER BY name;")

        types = []
        for type in cur.fetchall():
            t = {
                'test_type_id':     type['test_type_id'],
                'name':             type['name']
            }
            types.append(t)

        db.disconnect()

        return types

@cherrypy.tools.json_out()
class Schedule:
    exposed = True
    def GET(self):
        """ Return JSON of schedules
        """
        db = DB()
        cur = db.connect(settings.DSN)
        cur.execute("SELECT schedule_id, name FROM pq_schedule ORDER BY name;")

        schedules = []
        for schedule in cur.fetchall():
            s = {
                'schedule_id':      schedule['schedule_id'],
                'name':             schedule['name']
            }
            schedules.append(s)

        db.disconnect()

        return schedules

class JSON(object): 
    def GET(self):
        raise HTTPError(404)

class Pyqual:
    exposed = True
    j = JSON()
    j.test = Test()
    #j.test = PqTest()
    @cherrypy.expose
    def GET(self):
        """ Main page
        """
        f = open(settings.APP_ROOT + '/templates/main.html')
        return f.read()

cherrypy.quickstart(Pyqual(), '', settings.CP_CONFIG)
#cherrypy.quickstart(PqJson(), '/j', settings.CP_CONFIG)
