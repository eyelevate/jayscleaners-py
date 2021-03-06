import datetime
import time
import sqlite3
import json
import urllib
from urllib import error, request, parse
from threading import Thread
from models.model import *

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))

table = 'companies'


class Company:
    id = None
    company_id = None
    name = None
    street = None
    suite = None
    city = None
    state = None
    zip = None
    email = None
    phone = None
    store_hours = None
    turn_around = None
    api_token = None
    payment_gateway_id = None
    payment_api_login = None
    deleted_at = None
    created_at = now
    updated_at = now
    server_time = unix
    server_at = None

    def __init__(self):
        """Create the database and the table if they do not exist"""
        self._setUp()

    def retrieve(self, company_id, *args, **kwargs):
        url = 'http://www.jayscleaners.com/admins/api/company-grab'
        # attempt to connect to server
        data = parse.urlencode({'company_id': company_id}).encode('utf-8')
        req = request.Request(url=url, data=data)  # this will make the method "POST"
        try:
            # r = request.urlopen(url)
            r = request.urlopen(req)
            data_1 = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
            if data_1['status'] is 0:
                return False
            else:
                self.company_id = data_1['data']['id']
                self.id = data_1['data']['id']
                self.name = data_1['data']['name']
                self.street = data_1['data']['street']
                self.city = data_1['data']['city']
                self.state = data_1['data']['state']
                self.zip = data_1['data']['zip']
                self.email = data_1['data']['email']
                self.phone = data_1['data']['phone']
                self.store_hours = data_1['data']['store_hours']
                self.turn_around = data_1['data']['turn_around']
                self.api_token = data_1['data']['api_token']
                self.payment_gateway_id = data_1['data']['payment_gateway_id']
                self.payment_api_login = data_1['data']['payment_api_login']
                self.deleted_at = None
                self.server_time = unix
                self.server_at = unix
                result = self.find()
                if result is False:
                    self.add()
                else:
                    self.update()
                return data_1['data']

        except urllib.error.URLError as e:
            print(e.reason)  # could not save this time around because no internet, move on
            return False

    def create_table(self):
        table_schema = ', '.join([PrimaryKeyField(column='id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  CharField(column='name', max_length=100).data_type(),
                                  CharField(column='street', max_length=200).data_type(),
                                  CharField(column='suite', max_length=20).data_type(),
                                  CharField(column='city', max_length=20).data_type(),
                                  CharField(column='state', max_length=20).data_type(),
                                  CharField(column='zip', max_length=10).data_type(),
                                  CharField(column='email', max_length=200).data_type(),
                                  CharField(column='phone', max_length=20).data_type(),
                                  TextField(column='store_hours').data_type(),
                                  TextField(column='turn_around').data_type(),
                                  CharField(column='api_token', max_length=100).data_type(),
                                  TextField(column='payment_gateway_id').data_type(),
                                  TextField(column='payment_api_login').data_type(),
                                  TextField(column='deleted_at').data_type(),
                                  TextField(column='created_at').data_type(),
                                  TextField(column='updated_at').data_type(),
                                  TextField(column='server_at').data_type()
                                  ])
        self.c.execute('''CREATE TABLE IF NOT EXISTS {t} ({ts})'''.format(t=table, ts=table_schema))
        self.conn.commit()
        self._tearDown()

    def add(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        self.created_at = now
        self.c.execute('''INSERT INTO {t}
(company_id,name,street,suite,city,state,zip,email,phone,store_hours,turn_around,api_token,payment_gateway_id,payment_api_login,created_at,updated_at) VALUES
(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.company_id,
                                                       self.name,
                                                       self.street,
                                                       self.suite,
                                                       self.city,
                                                       self.state,
                                                       self.zip,
                                                       self.email,
                                                       self.phone,
                                                       self.store_hours,
                                                       self.turn_around,
                                                       self.api_token,
                                                       self.payment_gateway_id,
                                                       self.payment_api_login,
                                                       self.created_at,
                                                       self.updated_at)
                       )

        self.conn.commit()
        self._tearDown()
        return True

    def add_special(self):
        self.c.execute('''INSERT INTO {t}
(company_id,name,street,suite,city,state,zip,email,phone,store_hours,turn_around,api_token,payment_gateway_id,payment_api_login,created_at,updated_at) VALUES
(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.company_id,
                                                       self.name,
                                                       self.street,
                                                       self.suite,
                                                       self.city,
                                                       self.state,
                                                       self.zip,
                                                       self.email,
                                                       self.phone,
                                                       self.store_hours,
                                                       self.turn_around,
                                                       self.api_token,
                                                       self.payment_gateway_id,
                                                       self.payment_api_login,
                                                       self.created_at,
                                                       self.updated_at)
                       )

        self.conn.commit()
        self._tearDown()
        return True


    def put(self, where=False, data=False):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        sql = '''UPDATE {t} SET '''.format(t=table)
        if len(data) > 0:
            for key, value in data.items():
                if key == 'store_hours':
                    sql += '''{k} = '{v}', '''.format(k=key, v=json.dumps(value))
                else:
                    sql += '''{k} = "{v}", '''.format(k=key, v=value)
            sql += '''updated_at = "{v}" '''.format(v=self.updated_at)
        sql += '''WHERE '''
        idx = 0
        if len(where) > 0:
            for key, value in where.items():
                idx += 1
                if idx == len(where):
                    sql += '''{k} = {v}'''.format(k=key, v=value)
                else:
                    sql += '''{k} = {v} AND '''.format(k=key, v=value)

        self.c.execute(sql)
        self.conn.commit()
        self._tearDown()
        return True

    def update(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        self.c.execute('''UPDATE {t} SET company_id = ?, name = ?, street = ?, suite = ?, city = ?, state = ?, zip = ?,
email = ?, phone = ?, store_hours = ?, turn_around = ?, api_token = ?, payment_gateway_id = ?, payment_api_login = ?,
updated_at = ?, server_at = ? WHERE id = ?'''.format(
            t=table),
            (self.company_id,
             self.name,
             self.street,
             self.suite,
             self.city,
             self.state,
             self.zip,
             self.email,
             self.phone,
             self.store_hours,
             self.turn_around,
             self.api_token,
             self.payment_gateway_id,
             self.payment_api_login,
             self.updated_at,
             self.server_at,
             self.id)
        )

        self.conn.commit()
        self._tearDown()
        return True

    def update_special(self):
        self.c.execute('''UPDATE {t} SET company_id = ?, name = ?, street = ?, suite = ?, city = ?, state = ?, zip = ?,
email = ?, phone = ?, store_hours = ?, turn_around = ?, api_token = ?, payment_gateway_id = ?, payment_api_login = ?,
updated_at = ?, server_at = ? WHERE id = ?'''.format(
            t=table),
            (self.company_id,
             self.name,
             self.street,
             self.suite,
             self.city,
             self.state,
             self.zip,
             self.email,
             self.phone,
             self.store_hours,
             self.turn_around,
             self.api_token,
             self.payment_gateway_id,
             self.payment_api_login,
             self.updated_at,
             self.server_at,
             self.id)
        )

        self.conn.commit()
        self._tearDown()
        return True

    def find(self):
        self._setUp()
        try:
            self.c.execute("""SELECT * FROM {t} WHERE deleted_at is null AND id = ?""".format(table), (str(self.id)))
            self.conn.commit()
        except ValueError:
            return "Could not find the company with that id"
        finally:
            fetch = self.c.fetchone()
            self._tearDown
            return fetch

        return False

    def first(self, data=False):
        if data:
            sql = '''SELECT * FROM {t} WHERE deleted_at is null AND '''.format(t=table)
            idx = 0
            for key, value in data.items():
                idx += 1
                if idx == len(data):
                    sql += '''{k} = {v}'''.format(k=key, v=value)
                elif idx < len(data):
                    sql += '''{k} = {v} AND '''.format(k=key, v=value)

            self.c.execute(sql)
            self.conn.commit()
            fetch = self.c.fetchone()
            self._tearDown()
            return fetch
        else:
            self._tearDown()
            return False

    def where(self, data=False, deleted_at=True, set=False):
        if data:
            sql = '''SELECT * FROM {t} WHERE '''.format(t=table)
            idx = 0
            order_by = False
            limit = False
            if 'ORDER_BY' in data:
                order_by = data['ORDER_BY']
                del (data['ORDER_BY'])
            if 'LIMIT' in data:
                limit = data['LIMIT']
                del (data['LIMIT'])

            for key, value in data.items():
                idx += 1
                if isinstance(value, dict):
                    for oper, val in value.items():
                        if idx == len(data):
                            sql += '''{k} {o} {v}'''.format(k=key, o=oper, v=val)

                        elif idx < len(data):
                            sql += '''{k} {o} {v} AND '''.format(k=key, o=oper, v=val)

                else:
                    if idx == len(data):
                        if value is None:
                            sql += '''{k} is null'''.format(k=key)
                        else:
                            sql += '''{k} = {v}'''.format(k=key, v=value)
                    elif idx < len(data):
                        if value is None:
                            sql += '''{k} is null AND '''.format(k=key)
                        else:
                            sql += '''{k} = {v} AND '''.format(k=key, v=value)

            sql += ' AND deleted_at is null' if deleted_at else ''

            if order_by:
                sql += ''' ORDER BY {} '''.format(order_by)

            if limit:
                sql += '''LIMIT {}'''.format(limit)

            self.c.execute(sql)
            self.conn.commit()
            
            if set:
                companies = self.c.fetchall()
                if companies:
                    for company in companies:
                        self.id = company['id']
                        self.company_id = company['company_id']
                        self.name = company['name']
                        self.street = company['street']
                        self.suite = company['suite']
                        self.city = company['city']
                        self.state = company['state']
                        self.zip = company['zip']
                        self.email = company['email']
                        self.phone = company['phone']
            fetch = self.c.fetchall()
            self._tearDown()
            return fetch
        
        
        else:
            return False

    def like(self, data=False, deleted_at=True):
        if data:
            sql = '''SELECT * FROM {t} WHERE '''.format(t=table)
            idx = 0
            order_by = False
            limit = False
            if 'ORDER_BY' in data:
                order_by = data['ORDER_BY']
                del (data['ORDER_BY'])
            if 'LIMIT' in data:
                limit = data['LIMIT']
                del (data['LIMIT'])
            for key, value in data.items():
                idx += 1
                if idx == len(data):
                    if value is None:
                        sql += '''{k} is null'''.format(k=key)
                    else:
                        sql += '''{k} LIKE {v}'''.format(k=key, v=value)
                elif idx < len(data):
                    if value is None:
                        sql += '''{k} is null AND '''.format(k=key)
                    else:
                        sql += '''{k} LIKE {v} AND '''.format(k=key, v=value)

            sql += ' AND deleted_at is null ' if deleted_at else ''
            if order_by:
                sql += ''' ORDER BY {} '''.format(order_by)

            if limit:
                sql += '''LIMIT {}'''.format(limit)

            self.c.execute(sql)
            self.conn.commit()
            fetch = self.c.fetchall()
            self._tearDown()
            return fetch
        else:
            self._tearDown()
            return False

    def delete(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        if self.id:

            self.c.execute("""UPDATE {t} SET deleted_at = ?, updated_at = ? WHERE id = ?""".format(table),
                           (self.updated_at,
                            self.updated_at,
                            self.id)
                           )

            self.conn.commit()
            self._tearDown()
            return True 
        else:
            self._tearDown()
            return False

    def server_at_update(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        sql = '''UPDATE {t} SET server_at = "{time}" where id > {id}'''.format(t=table,time=now,id='0')

        self.c.execute(sql)
        self.conn.commit()
        self._tearDown()
        return True

    def server_at_update_special(self, server_at):
        sql = '''UPDATE {t} SET server_at = "{time}" where id > {id}'''.format(t=table,time=server_at,id='0')

        self.c.execute(sql)
        self.conn.commit()
        self._tearDown()
        return True

    def get_store_hours(self, company_id):
        companies = self.where({'company_id': company_id})
        if companies:
            for company in companies:
                store_hours = json.loads(company['store_hours'])
        else:
            store_hours = False
        return store_hours

    def prepareCompanyList(self):
        companies = self.where({'id':{'>':0}})
        list = []
        if companies:
            for company in companies:
                list.append(company['name'])
        return list

    def truncate(self):
        self.c.execute("""DELETE FROM {t}""".format(t=table))
        self.conn.commit()
        self.c.execute("""DELETE FROM SQLITE_SEQUENCE WHERE name='{t}'""".format(t=table))
        self.conn.commit()
        self._tearDown()
        
    def _setUp(self):
        try:
            self.conn = sqlite3.connect('./db/jayscleaners.db')
        except sqlite3.OperationalError:
            self.conn = sqlite3.connect('jayscleaners.db')
        self.conn.row_factory = dict_factory
        self.c = self.conn.cursor()
        
    def _tearDown(self):
        self.c.close()
        self.conn.close()
