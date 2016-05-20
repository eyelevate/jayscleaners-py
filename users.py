import datetime
import time
import sqlite3
from model import *

unix = time.time()
now = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
table = 'users'


class User:
    id = None
    user_id = None
    company_id = None
    username = None
    first_name = None
    last_name = None
    street = None
    suite = None
    city = None
    state = None
    zipcode = None
    email = None
    phone = None
    intercom = None
    concierge_name = None
    concierge_number = None
    special_instructions = None
    shirt_old = None
    shirt = None
    delivery = None
    profile_id = None
    payment_status = None
    payment_id = None
    token = None
    api_token = None
    reward_status = None
    reward_points = None
    account = None
    starch = None
    important_memo = None
    invoice_memo = None
    password = None
    role_id = None
    deleted_at = None
    remember_token = None
    created_at = now
    updated_at = now

    def __init__(self):
        """Create the database and the table if they do not exist"""
        self.conn = sqlite3.connect('./db/jayscleaners.db')
        self.conn.row_factory = dict_factory
        self.c = self.conn.cursor()

    def create_table(self):
        table_schema = ', '.join([PrimaryKeyField(column='id').data_type(),
                                  IntegerField(column='user_id').data_type(),
                                  IntegerField(column='company_id').data_type(),
                                  CharField(column='username', max_length=100).data_type(),
                                  CharField(column='first_name', max_length=100).data_type(),
                                  CharField(column='last_name', max_length=100).data_type(),
                                  CharField(column='street', max_length=200).data_type(),
                                  CharField(column='suite', max_length=20).data_type(),
                                  CharField(column='city', max_length=100).data_type(),
                                  CharField(column='state', max_length=20).data_type(),
                                  CharField(column='zipcode', max_length=10).data_type(),
                                  CharField(column='email', max_length=255).data_type(),
                                  CharField(column='phone', max_length=20).data_type(),
                                  CharField(column='intercom', max_length=20).data_type(),
                                  CharField(column='concierge_name', max_length=100).data_type(),
                                  CharField(column='concierge_number', max_length=100).data_type(),
                                  TextField(column='special_instructions').data_type(),
                                  CharField(column='shirt_old', max_length=10).data_type(),
                                  IntegerField(column='shirt').data_type(),
                                  IntegerField(column='delivery').data_type(),
                                  CharField(column='profile_id', max_length=100).data_type(),
                                  CharField(column='payment_id', max_length=100).data_type(),
                                  IntegerField(column='payment_status').data_type(),
                                  CharField(column='token', max_length=8).data_type(),
                                  CharField(column='api_token', max_length=20).data_type(),
                                  IntegerField(column='reward_status').data_type(),
                                  IntegerField(column='reward_points').data_type(),
                                  IntegerField(column='account').data_type(),
                                  IntegerField(column='starch').data_type(),
                                  TextField(column='important_memo').data_type(),
                                  TextField(column='invoice_memo').data_type(),
                                  CharField(column='password', max_length=60).data_type(),
                                  IntegerField(column='role_id').data_type(),
                                  CharField(column='remember_token', max_length=60).data_type(),
                                  TextField(column='deleted_at').data_type(),
                                  TextField(column='created_at').data_type(),
                                  TextField(column='updated_at').data_type(),
                                  ])

        self.c.execute('''CREATE TABLE IF NOT EXISTS {t} ({ts})'''.format(t=table, ts=table_schema))
        self.conn.commit()

    def add(self):

        self.c.execute('''INSERT INTO {t}(user_id,company_id,username,first_name,last_name,street,suite,city,state,
zipcode,email,phone,intercom,concierge_name,concierge_number,special_instructions,shirt_old,shirt,delivery,profile_id,
payment_id,payment_status,token,api_token,reward_status,reward_points,account,starch,important_memo,invoice_memo,
password,role_id,remember_token,created_at,updated_at)
VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''.format(t=table),
                       (self.user_id,
                        self.company_id,
                        self.username,
                        self.first_name,
                        self.last_name,
                        self.street,
                        self.suite,
                        self.city,
                        self.state,
                        self.zipcode,
                        self.email,
                        self.phone,
                        self.intercom,
                        self.concierge_name,
                        self.concierge_number,
                        self.special_instructions,
                        self.shirt_old,
                        self.shirt,
                        self.delivery,
                        self.profile_id,
                        self.payment_id,
                        self.payment_status,
                        self.token,
                        self.api_token,
                        self.reward_status,
                        self.reward_points,
                        self.account,
                        self.starch,
                        self.important_memo,
                        self.invoice_memo,
                        self.password,
                        self.role_id,
                        self.remember_token,
                        self.created_at,
                        self.updated_at)
                       )

        self.conn.commit()
        return True

    def update(self):

        self.c.execute('''UPDATE {t} SET user_id = ?, company_id = ?, username = ?, first_name = ?, last_name = ?,
street = ?, suite = ?, city = ?, state = ?, zipcode = ?, email = ?, phone = ?, intercom = ?, concierge_name = ?,
concierge_number = ?, special_instructions = ?, shirt_old = ?, shirt = ?, delivery = ?, profile_id = ?, payment_id = ?,
payment_status = ?, token = ?, api_token = ?, reward_status = ?, reward_points = ?, account = ?, starch = ?,
important_memo = ?, invoice_memo = ?, password = ?, role_id = ?, remember_token = ?, updated_at = ?
WHERE id = ?'''.format(t=table), (self.user_id,
                                  self.company_id,
                                  self.username,
                                  self.first_name,
                                  self.last_name,
                                  self.street,
                                  self.suite,
                                  self.city,
                                  self.state,
                                  self.zipcode,
                                  self.email,
                                  self.phone,
                                  self.intercom,
                                  self.concierge_name,
                                  self.concierge_number,
                                  self.special_instructions,
                                  self.shirt_old,
                                  self.shirt,
                                  self.delivery,
                                  self.profile_id,
                                  self.payment_id,
                                  self.payment_status,
                                  self.token,
                                  self.api_token,
                                  self.reward_status,
                                  self.reward_points,
                                  self.account,
                                  self.starch,
                                  self.important_memo,
                                  self.invoice_memo,
                                  self.password,
                                  self.role_id,
                                  self.remember_token,
                                  self.updated_at,
                                  self.id)
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
            if order_by:
                sql += ''' ORDER BY {} '''.format(order_by)

            if limit:
                sql += '''LIMIT {}'''.format(limit)
            self.c.execute(sql)
            self.conn.commit()
            return self.c.fetchall()
        else:
            return False

    def auth(self, username = False, password = False):
        self.c.execute('''SELECT * FROM USERS WHERE username = ? and password = ?''',(username,password))
        self.conn.commit()
        if len(self.c.fetchall()) > 0:
            # check to see if role_is admin
            for key, value in self.c.fetchall().items():
                print(value)

            return True
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
