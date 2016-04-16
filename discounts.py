import datetime
import time
import sqlite3
from model import *

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
table = 'discounts'

class Discount:
    id = None
    discount_id = None
    company_id = None
    inventory_id = None
    inventory_item_id = None
    name = None
    type = None
    discount = None
    rate = None
    end_time = None
    start_date = None
    end_date = None
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
                                  IntegerField(column='discount_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  IntegerField(column='inventory_id').data_type(),
                                  IntegerField(column='inventory_item_id').data_type(),
                                  CharField(column='name', max_length=100).data_type(),
                                  IntegerField(column='type').data_type(),
                                  FloatField(column="discount").data_type(),
                                  FloatField(column="rate").data_type(),
                                  CharField(column='end_time', max_length=100).data_type(),
                                  TextField(column='start_date').data_type(),
                                  TextField(column='end_date').data_type(),
                                  IntegerField(column='status').data_type(),
                                  TextField(column='deleted_at').data_type(),
                                  TextField(column='created_at').data_type(),
                                  TextField(column='updated_at').data_type(),
                                  ])

        self.c.execute('''CREATE TABLE IF NOT EXISTS {t} ({ts})'''.format(t=table, ts=table_schema))
        self.conn.commit()

    def add(self):

        self.c.execute('''INSERT INTO {t}(discount_id,company_id,inventory_id,inventory_item_id,name,type,discount,rate,
end_time,start_date,end_date,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table),
                       (self.discount_id,
                        self.company_id,
                        self.inventory_id,
                        self.inventory_item_id,
                        self.name,
                        self.type,
                        self.discount,
                        self.rate,
                        self.end_time,
                        self.start_date,
                        self.end_date,
                        self.status,
                        self.created_at,
                        self.updated_at)
                       )

        self.conn.commit()
        return True

    def update(self):

        self.c.execute('''UPDATE {t} SET discount_id = ?, company_id = ?, inventory_id = ?, inventory_item_id = ?,
name = ?, type = ?, discount = ?, rate = ?, end_time = ?, start_date = ?, end_date = ?, status = ?, updated_at = ?
WHERE discount_id = ?'''.format(t=table),(self.discount_id,
                                          self.company_id,
                                          self.inventory_id,
                                          self.inventory_item_id,
                                          self.name,
                                          self.type,
                                          self.discount,
                                          self.rate,
                                          self.end_time,
                                          self.start_date,
                                          self.end_date,
                                          self.status,
                                          self.updated_at,
                                          self.discount_id)
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

    class Meta:
        database = db