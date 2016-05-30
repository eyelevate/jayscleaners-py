import datetime
import time
import sqlite3
from model import *

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
table = 'reward_transactions'


class RewardTransaction:
    id = None
    reward_id = None
    transaction_id = None
    customer_id = None
    employee_id = None
    company_id = None
    type = None
    points = None
    credited = None
    reduced = None
    running_total = None
    reason = None
    name = None
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
                                  IntegerField(column='reward_id').data_type(),
                                  IntegerField(column='transaction_id').data_type(),
                                  IntegerField(column='customer_id').data_type(),
                                  IntegerField(column='employee_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  IntegerField(column='type').data_type(),
                                  IntegerField(column='points').data_type(),
                                  IntegerField(column='credited').data_type(),
                                  IntegerField(column='reduced').data_type(),
                                  IntegerField(column='running_total').data_type(),
                                  IntegerField(column='reason').data_type(),
                                  CharField(column='name', max_length=100).data_type(),
                                  IntegerField(column='status').data_type(),
                                  TextField(column='deleted_at').data_type(),
                                  TextField(column='created_at').data_type(),
                                  TextField(column='updated_at').data_type(),
                                  ])

        self.c.execute('''CREATE TABLE IF NOT EXISTS {t} ({ts})'''.format(t=table, ts=table_schema))
        self.conn.commit()

    def add(self):

        self.c.execute('''INSERT INTO {t}(reward_id,transaction_id,customer_id,employee_id,company_id,type,points,
credited,reduced,running_total,reason,name,status,created_at,updated_at)
VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table), (self.reward_id,
                                                           self.transaction_id,
                                                           self.customer_id,
                                                           self.employee_id,
                                                           self.company_id,
                                                           self.type,
                                                           self.points,
                                                           self.credited,
                                                           self.reduced,
                                                           self.running_total,
                                                           self.reason,
                                                           self.name,
                                                           self.status,
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

        self.c.execute('''UPDATE {t} SET reward_id = ?, transaction_id = ?, customer_id = ?, employee_id = ?,
company_id = ?, type = ?, points = ?, credited = ?, reduced = ?, running_total = ?, reason = ?, name = ?, status = ?,
updated_at = ? WHERE id = ?'''.format(t=table), (self.reward_id,
                                                 self.transaction_id,
                                                 self.customer_id,
                                                 self.employee_id,
                                                 self.company_id,
                                                 self.type,
                                                 self.points,
                                                 self.credited,
                                                 self.reduced,
                                                 self.running_total,
                                                 self.reason,
                                                 self.name,
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

    def where(self, data=False):
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

                sql += ' AND deleted_at is null'

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

            sql += ' AND deleted_at is null '

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
