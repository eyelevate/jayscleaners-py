import datetime
import time
import sqlite3
from model import *

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
table = 'invoice_items'


class InvoiceItem(Model):
    id = None
    invoice_items_id = None
    invoice_id = None
    item_id = None
    company_id = None
    customer_id = None
    quantity = None
    color = None
    memo = None
    pretax = None
    tax = None
    total = None
    status = None
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
                                  IntegerField(column='invoice_items_id').data_type(),
                                  IntegerField(column='invoice_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  IntegerField(column='customer_id').data_type(),
                                  IntegerField(column='quantity').data_type(),
                                  IntegerField(column='color').data_type(),
                                  TextField(column='memo').data_type(),
                                  FloatField(column='pretax').data_type(),
                                  FloatField(column='tax').data_type(),
                                  FloatField(column='total').data_type(),
                                  IntegerField(column='status').data_type(),
                                  TextField(column='deleted_at').data_type(),
                                  TextField(column='created_at').data_type(),
                                  TextField(column='updated_at').data_type(),
                                  ])

        self.c.execute('''CREATE TABLE IF NOT EXISTS {t} ({ts})'''.format(t=table, ts=table_schema))
        self.conn.commit()

    def add(self):

        self.c.execute('''INSERT INTO {t}(invoice_items_id,invoice_id,company_id,customer_id,quantity,color,memo,
pretax,tax,total,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table),
                       (self.invoice_items_id,
                        self.invoice_id,
                        self.company_id,
                        self.customer_id,
                        self.quantity,
                        self.color,
                        self.memo,
                        self.pretax,
                        self.tax,
                        self.total,
                        self.status,
                        self.created_at,
                        self.updated_at)
                       )

        self.conn.commit()
        return True

    def update(self):

        self.c.execute('''UPDATE {t} SET invoice_items_id = ?, invoice_id = ?, company_id = ?, customer_id = ?,
quantity = ?, color = ?, memo = ?, pretax = ?, tax = ?, total = ?, status = ?, updated_at = ?
WHERE invoice_items_id = ?'''.format(t=table), (self.invoice_items_id,
                                                self.invoice_id,
                                                self.company_id,
                                                self.customer_id,
                                                self.quantity,
                                                self.color,
                                                self.memo,
                                                self.pretx,
                                                self.tax,
                                                self.total,
                                                self.status,
                                                self.updated_at,
                                                self.invoice_items_id)
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
