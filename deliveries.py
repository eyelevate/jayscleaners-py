import datetime
import time
import sqlite3
from model import *

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
table = 'deliveries'


class Delivery:
    id = None
    delivery_id = None
    company_id = None
    route_name = None
    day = None
    delivery_limit = None
    start_time = None
    end_time = None
    zipcode = None
    blackout = None
    reward_points = None
    deleted_at = None
    created_at = now
    updated_at = now

    def __init__(self):
        """Create the database and the table if they do not exist"""
        self.conn = sqlite3.connect('./db/jayscleaners.db')
        self.conn.row_factory = dict_factory
        self.c = self.conn.cursor()

    def create_table(self):
        table_schema = ', '.join([PrimaryKeyField(column='id').data_type(),
                                  IntegerField(column='delivery_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  CharField(column='route_name', max_length=100).data_type(),
                                  CharField(column='day', max_length=100).data_type(),
                                  CharField(column='delivery_limit', max_length=20).data_type(),
                                  CharField(column='start_time', max_length=25).data_type(),
                                  CharField(column='end_time', max_length=25).data_type(),
                                  TextField(column='zipcode').data_type(),
                                  TextField(column='blackout').data_type(),
                                  IntegerField(column='reward_points').data_type(),
                                  TextField(column='deleted_at').data_type(),
                                  TextField(column='created_at').data_type(),
                                  TextField(column='updated_at').data_type(),
                                  ])

        self.c.execute('''CREATE TABLE IF NOT EXISTS {t} ({ts})'''.format(t=table, ts=table_schema))
        self.conn.commit()

    def add(self):

        self.c.execute('''INSERT INTO {t}(delivery_id,company_id,route_name,day,delivery_limit,start_time,end_time,zipcode,
blackout,reward_points,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.delivery_id,
                                                                                                     self.company_id,
                                                                                                     self.route_name,
                                                                                                     self.day,
                                                                                                     self.delivery_limit,
                                                                                                     self.start_time,
                                                                                                     self.end_time,
                                                                                                     self.zipcode,
                                                                                                     self.blackout,
                                                                                                     self.reward_points,
                                                                                                     self.created_at,
                                                                                                     self.updated_at)
                       )

        self.conn.commit()
        return True

    def update(self):

        self.c.execute('''UPDATE {t} SET delivery_id = ?, company_id = ?, route_name = ?, day = ?, delivery_limit = ?,
start_time = ?, end_time = ?, zipcode = ?, blackout = ?, reward_points = ?, updated_at = ?
WHERE id = ?'''.format(t=table), (self.delivery_id,
                                  self.company_id,
                                  self.route_name,
                                  self.day,
                                  self.delivery_limit,
                                  self.start_time,
                                  self.end_time,
                                  self.zipcode,
                                  self.blackout,
                                  self.reward_points,
                                  self.updated_at,
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
