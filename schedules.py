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
    pickup_delivery_id = None
    pickup_date = None
    dropoff_delivery_id = None
    dropoff_date = None
    special_instructions = None
    type = None
    token = None
    status = None
    deleted_at = None
    created_at = None
    updated_at = None

    def __init__(self):
        """Create the database and the table if they do not exist"""
        self.conn = sqlite3.connect('./db/jayscleaners.db')
        self.conn.row_factory = dict_factory
        self.c = self.conn.cursor()

    def create_table(self):
        table_schema = ', '.join([PrimaryKeyField(column='id').data_type(),
                                  IntegerField(column='schedule_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  IntegerField(column='pickup_delivery_id').data_type(),
                                  TextField(column='pickup_date').data_type(),
                                  IntegerField(column='dropoff_delivery_id').data_type(),
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

        self.c.execute('''INSERT INTO {t}(schedule_id,company_id,pickup_delivery_id,pickup_date,dropoff_delivery_id,
dropoff_date,special_instructions,type,token,status,created_at,updated_at)
VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.schedule_id,
                                                       self.company_id,
                                                       self.pickup_delivery_id,
                                                       self.pickup_date,
                                                       self.dropoff_delivery_id,
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

    def update(self):

        self.c.execute('''UPDATE {t} SET schedule_id = ?, company_id = ?, pickup_delivery_id = ?, pickup_date = ?,
dropoff_delivery_id = ?, dropoff_date = ?, special_instructions = ?, type = ?, token = ?, status = ?, updated_at = ?
WHERE schedule_id = ?'''.format(t=table), (self.schedule_id,
                                           self.company_id,
                                           self.pickup_delivery_id,
                                           self.pickup_date,
                                           self.dropoff_delivery_id,
                                           self.dropoff_date,
                                           self.special_instructions,
                                           self.type,
                                           self.token,
                                           self.status,
                                           self.updated_at,
                                           self.schedule_id)
                       )

        self.conn.commit()
        return True

    def find(self):
        try:
            self.c.execute("""SELECT * FROM {t} WHERE id = ?""".format(table), (str(self.id)))
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
            for key, value in data.items():
                idx += 1
                if idx == len(data):
                    sql += '''{k} = {v}'''.format(k=key, v=value)
                elif idx < len(data):
                    sql += '''{k} = {v} AND '''.format(k=key, v=value)
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
