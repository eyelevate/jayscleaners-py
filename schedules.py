import datetime
import time
import sqlite3
from model import *

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
table = 'schedules'


class Schedule:
    id = None
    schedule_id = None
    company_id = None
    customer_id = None
    card_id = None
    pickup_delivery_id = None
    pickup_date = None
    pickup_address = None
    dropoff_delivery_id = None
    dropoff_date = None
    dropoff_address = None
    special_instructions = None
    type = None
    token = None
    status = None
    deleted_at = None
    created_at = None
    updated_at = None

    def __init__(self):
        """Create the database and the table if they do not exist"""
        try:
            self.conn = sqlite3.connect('./db/jayscleaners.db')
        except sqlite3.OperationalError:
            self.conn = sqlite3.connect('jayscleaners.db')
        self.conn.row_factory = dict_factory
        self.c = self.conn.cursor()

    def create_table(self):
        table_schema = ', '.join([PrimaryKeyField(column='id').data_type(),
                                  IntegerField(column='schedule_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  IntegerField(column='customer_id').data_type(),
                                  IntegerField(column='card_id').data_type(),
                                  IntegerField(column='pickup_delivery_id').data_type(),
                                  IntegerField(column='pickup_address').data_type(),
                                  TextField(column='pickup_date').data_type(),
                                  IntegerField(column='dropoff_delivery_id').data_type(),
                                  IntegerField(column='dropoff_address').data_type(),
                                  TextField(column='dropoff_date').data_type(),
                                  TextField(column='special_instructions').data_type(),
                                  CharField(column='type', max_length=20).data_type(),
                                  CharField(column='token', max_length=8).data_type(),
                                  IntegerField(column='status').data_type(),
                                  TextField(column='deleted_at').data_type(),
                                  TextField(column='created_at').data_type(),
                                  TextField(column='updated_at').data_type(),
                                  ])

        self.c.execute('''CREATE TABLE IF NOT EXISTS {t} ({ts})'''.format(t=table, ts=table_schema))
        self.conn.commit()

    def add(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        self.created_at = now
        self.c.execute('''INSERT INTO {t}(schedule_id,company_id,customer_id, card_id,pickup_delivery_id,
pickup_address,pickup_date,dropoff_delivery_id, dropoff_address, dropoff_date,special_instructions,type,token,status,
created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.schedule_id,
                                                                                    self.company_id,
                                                                                    self.customer_id,
                                                                                    self.card_id,
                                                                                    self.pickup_delivery_id,
                                                                                    self.pickup_address,
                                                                                    self.pickup_date,
                                                                                    self.dropoff_delivery_id,
                                                                                    self.dropoff_address,
                                                                                    self.dropoff_date,
                                                                                    self.special_instructions,
                                                                                    self.type,
                                                                                    self.token,
                                                                                    self.status,
                                                                                    self.created_at,
                                                                                    self.updated_at)
                       )

        self.conn.commit()
        return True

    def add_special(self):
        self.c.execute('''INSERT INTO {t}(schedule_id,company_id,customer_id, card_id,pickup_delivery_id,
pickup_address,pickup_date,dropoff_delivery_id, dropoff_address, dropoff_date,special_instructions,type,token,status,
created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.schedule_id,
                                                                                    self.company_id,
                                                                                    self.customer_id,
                                                                                    self.card_id,
                                                                                    self.pickup_delivery_id,
                                                                                    self.pickup_address,
                                                                                    self.pickup_date,
                                                                                    self.dropoff_delivery_id,
                                                                                    self.dropoff_address,
                                                                                    self.dropoff_date,
                                                                                    self.special_instructions,
                                                                                    self.type,
                                                                                    self.token,
                                                                                    self.status,
                                                                                    self.created_at,
                                                                                    self.updated_at)
                       )

        self.conn.commit()
        return True

    def put(self, where=False, data=False):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        sql = '''UPDATE {t} SET '''.format(t=table)
        if len(data) > 0:
            for key, value in data.items():
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

        return True

    def update(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        self.c.execute('''UPDATE {t} SET schedule_id = ?, company_id = ?, customer_id = ?, card_id = ?,
pickup_delivery_id = ?, pickup_address = ?, pickup_date = ?, dropoff_delivery_id = ?, dropoff_address= ?,
dropoff_date = ?, special_instructions = ?, type = ?, token = ?, status = ?, updated_at = ?
WHERE id = ?'''.format(t=table), (self.schedule_id,
                                  self.company_id,
                                  self.customer_id,
                                  self.card_id,
                                  self.pickup_delivery_id,
                                  self.pickup_address,
                                  self.pickup_date,
                                  self.dropoff_delivery_id,
                                  self.dropoff_address,
                                  self.dropoff_date,
                                  self.special_instructions,
                                  self.type,
                                  self.token,
                                  self.status,
                                  self.updated_at,
                                  self.id)
                       )

        self.conn.commit()
        return True

    def update_special(self):
        self.c.execute('''UPDATE {t} SET schedule_id = ?, company_id = ?, customer_id = ?, card_id = ?,
pickup_delivery_id = ?, pickup_address = ?, pickup_date = ?, dropoff_delivery_id = ?, dropoff_address= ?,
dropoff_date = ?, special_instructions = ?, type = ?, token = ?, status = ?, updated_at = ?
WHERE id = ?'''.format(t=table), (self.schedule_id,
                                  self.company_id,
                                  self.customer_id,
                                  self.card_id,
                                  self.pickup_delivery_id,
                                  self.pickup_address,
                                  self.pickup_date,
                                  self.dropoff_delivery_id,
                                  self.dropoff_address,
                                  self.dropoff_date,
                                  self.special_instructions,
                                  self.type,
                                  self.token,
                                  self.status,
                                  self.updated_at,
                                  self.id)
                       )

        self.conn.commit()
        return True

    def find(self):
        try:
            self.c.execute("""SELECT * FROM {t} WHERE deleted_at is null AND id = ?""".format(table), (str(self.id)))
            self.conn.commit()
        except ValueError:
            return "Could not find the company with that id"
        finally:
            return self.c.fetchone()

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
            return self.c.fetchone()
        else:
            return False

    def where(self, data=False, deleted_at=True):
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
            return self.c.fetchall()
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
            return self.c.fetchall()
        else:
            return False

    def delete(self):
        unix = time.time()
        now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
        self.updated_at = now
        if self.id:

            self.c.execute("""UPDATE {t} SET deleted_at = ?, updated_at = ? WHERE id = ?""".format(t=table),
                           (self.updated_at,
                            self.updated_at,
                            self.id)
                           )

            self.conn.commit()

            return True
        else:
            return False

    def truncate(self):

        self.c.execute("""DELETE FROM {t}""".format(t=table))
        self.conn.commit()
        self.c.execute("""DELETE FROM SQLITE_SEQUENCE WHERE name='{t}'""".format(t=table))
        self.conn.commit()

    def close_connection(self):
        self.c.close()
        self.conn.close()


    def getStatus(self, data):
        status = ''
        if data:
            if data is 1:
                status = 'Delivery Scheduled'
            elif data is 2:
                status = 'En-route Pickup'
            elif data is 3:
                status = 'Picked Up'
            elif data is 4:
                status = 'Processing'
            elif data is 5:
                status = 'Invoice Paid'
            elif data is 6:
                status = 'Cancelled by customer'
            elif data is 7:
                status = 'Delayed - Processing not complete'
            elif data is 8:
                status = 'Delayed - Customer unavailable for pickup'
            elif data is 9:
                status = 'Delayed - Customer unavailable for dropoff'
            elif data is 10:
                status = 'Delayed - Card on file processing error'
            elif data is 11:
                status = 'En-route Dropoff - invoice paid'
            else:
                status = 'Dropped Off. Thank You!'

        return status