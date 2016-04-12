from peewee import *

db = SqliteDatabase('db/memos.db')

class Memo(Model):

    id = PrimaryKeyField()
    memo_id = IntegerField(null=True)
    company_id = IntegerField(null=True)
    memo = CharField(max_length=100,null=True)
    ordered = IntegerField(null=True)
    status = IntegerField(null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)


    class Meta:
        database = db

def initialize():
    """Create the database and the table if they do not exist"""
    db.connect()
    db.create_tables([Memo],safe=True)
