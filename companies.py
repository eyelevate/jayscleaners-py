import datetime
import time
import sqlite3
from model import *

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
    deleted_at = None
    created_at = now
    updated_at = now
    server_time = unix
    server_at = None

    def __init__(self):
        """Create the database and the table if they do not exist"""
        self.conn = sqlite3.connect('./db/jayscleaners.db')
        self.conn.row_factory = dict_factory
        self.c = self.conn.cursor()
        self.create_table()

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
                                  TextField(column='deleted_at').data_type(),
                                  TextField(column='created_at').data_type(),
                                  TextField(column='updated_at').data_type(),
                                  TextField(column='server_at').data_type()
                                  ])

        self.c.execute('''CREATE TABLE IF NOT EXISTS {t} ({ts})'''.format(t=table, ts=table_schema))
        self.conn.commit()

    def add(self):

        self.c.execute('''INSERT INTO {t}
(company_id,name,street,suite,city,state,zip,email,phone,store_hours,turn_around,api_token,created_at,updated_at) VALUES
(?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.company_id,
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
                                                   self.created_at,
                                                   self.updated_at)
                       )

        self.conn.commit()
        return True

    def put(self, where = False, data = False):
        sql = '''UPDATE {t} SET '''.format(t=table)
        idx = 0
        if len(data) > 0:
            for key, value in data.items():
                idx += 1
                if idx == len(data):
                    sql += '''{k} = "{v}" '''.format(k=key, v=value)
                else:
                    sql += '''{k} = "{v}", '''.format(k=key, v=value)
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

        return True

    def update(self):

        self.c.execute('''UPDATE {t} SET company_id = ?, name = ?, street = ?, suite = ?, city = ?, state = ?, zip = ?,
email = ?, phone = ?, store_hours = ?, turn_around = ?, api_token = ?, updated_at = ?, server_at = ? WHERE id = ?'''.format(t=table),
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
                        self.updated_at,
                        self.server_at,
                        self.id)
                       )

        self.conn.commit()
        return True

    def find(self):
        try:
            self.c.execute("""SELECT * FROM {t} WHERE id = ?""".format(t=table), (str(self.id)))
            self.conn.commit()
        except ValueError:
            return "Could not find the company with that id"
        finally:
            return self.c.fetchone()

        return False

    def first(self, data=False):
        if data:
            sql = '''SELECT * FROM {t} WHERE '''.format(t=table)
            idx = 0
            for key, value in data.items():
                idx += 1
                if idx == len(data):
                    sql += '''{k} = {v}'''.format(k=key, v=value)
                elif idx < len(data):
                    sql += '''{k} = {v} AND '''.format(k=key, v=value)
            self.c.execute(sql)
            self.conn.commit()
            return self.c.fetchone()
        else:
            return False

    def where(self, data=False):
        if data:
            sql = '''SELECT * FROM {t} WHERE '''.format(t=table)
            idx = 0
            order_by = False
            limit = False
            if 'ORDER_BY' in data:
                order_by = data['ORDER_BY']
                del (data['ORDER_BY'])
                print('removed order_by {}'.format(order_by))
            if 'LIMIT' in data:
                limit = data['LIMIT']
                del (data['LIMIT'])
                print('removed limit {}'.format(limit))

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
            if order_by:
                sql += ''' ORDER BY {} '''.format(order_by)

            if limit:
                sql += '''LIMIT {}'''.format(limit)

            self.c.execute(sql)
            self.conn.commit()
            return self.c.fetchall()
        else:
            return False

    def like(self, data=False):
        if data:
            sql = '''SELECT * FROM {t} WHERE '''.format(t=table)
            idx = 0
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

            self.c.execute(sql)
            self.conn.commit()
            return self.c.fetchall()
        else:
            return False


    def delete(self):

        if self.id:

            self.c.execute("""UPDATE {t} SET deleted_at = ?, updated_at = ? WHERE id = ?""".format(table),
                           (self.updated_at,
                            self.updated_at,
                            self.id)
                           )

            self.conn.commit()

            return True
        else:
            return False

    def close_connection(self):
        self.c.close()
        self.conn.close()

