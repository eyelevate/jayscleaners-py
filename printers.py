from peewee import *

db = SqliteDatabase('db/printers.db')

class Printer(Model):

    id = PrimaryKeyField()
    printer_id = IntegerField(null=True)
    company_id = IntegerField(null=True)
    name = CharField(max_length=100,null=True)
    model = CharField(max_length=100, null=True)
    nick_name = CharField(max_length=100, null=True)
    type = IntegerField(null=True)
    status = IntegerField(null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)


    class Meta:
        database = db

def initialize():
    """Create the database and the table if they do not exist"""
    db.connect()
    db.create_tables([Priner],safe=True)