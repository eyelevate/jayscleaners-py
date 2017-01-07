import datetime
import time
import sqlite3
from random import choice
from string import digits
from model import *
from users import User

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
table = 'custids'


class Custid:
    id = None
    cust_id = None
    customer_id = None
    company_id = None
    mark = None
    status = None
    deleted_at = None
    created_at = now
    updated_at = now

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
                                  IntegerField(column='cust_id').data_type(),
                                  IntegerField(column='customer_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  TextField(column='mark').data_type(),
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
        self.c.execute('''INSERT INTO {t}(cust_id,customer_id,company_id,mark,status,created_at,updated_at)
VALUES(?,?,?,?,?,?,?)'''.format(t=table), (self.cust_id,
                                           self.customer_id,
                                           self.company_id,
                                           self.mark,
                                           self.status,
                                           self.created_at,
                                           self.updated_at)
                       )

        self.conn.commit()
        return True

    def put(self, where = False, data = False):
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
        self.c.execute('''UPDATE {t} SET cust_id = ?, customer_id = ?, company_id = ?, mark = ?, status = ?,
updated_at = ? WHERE id = ?'''.format(t=table), (self.cust_id,
                                                 self.customer_id,
                                                 self.company_id,
                                                 self.mark,
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

    def make_string(self, data):
        marks = []
        if len(data) > 0:
            for mrk in data:
                if mrk['mark']:
                    marks.append(str(mrk['mark']))
                else:
                    marks.append(str(mrk['cust_id']))

            return ', '.join(marks)
        else:
            return ''

    def create_customer_mark(self, last_name=False, customer_id=False, starch=False, random=False):
        mark = ''
        if last_name and customer_id and starch:
            # get the first character of the last name and capitalize it
            last_init = last_name[:1].capitalize()
            # add in the customer_id

            # get the first character of the starch preference and capitalize it
            starch_init = starch[:1].capitalize()

            mark = '{}{}{}'.format(last_init,customer_id,starch_init)

            # check to see if mark exists
            data = {'mark': '"{}"'.format(mark)}
            custid = self.where(data)
            if len(custid) > 0:
                # make_random = ''.join(choice(digits) for i in range(5))
                # mark_random = self.create_customer_mark(last_name=last_name, customer_id=make_random, starch=starch)
                return False
            else:
                return mark

    def getCustomerMark(self, customer_id):
        marks = self.where({'customer_id':customer_id})
        if marks:
            for m in marks:
                mark = m['mark']
                break
        else:
            users = User().where({'user_id':customer_id})
            if users:
                for user in users:
                    last_name = user['last_name'][:1].capitalize()
                    if user['starch'] is 1:
                        starch = 'N'
                    elif starch is 2:
                        starch = 'L'
                    elif starch is 3:
                        starch = 'M'
                    else:
                        starch = 'H'

                    mark = '{}{}{}'.format(last_name,str(customer_id),starch)
            else:
                return False
        print(mark)
        return mark



