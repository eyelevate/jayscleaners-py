from peewee import *

db = SqliteDatabase('db/custids.db')

class Custid(Model):
    id = PrimaryKeyField()
    cust_id = IntegerField(null=True)
    mark = TextField(null=True)
    status = IntegerField(null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)


    class Meta:
        database = db
