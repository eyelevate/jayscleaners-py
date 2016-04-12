from peewee import *

db = SqliteDatabase('db/colors.db')

class Color(Model):

    id = PrimaryKeyField()
    color_id = IntegerField(null=True)
    company_id = IntegerField()
    color = CharField(max_length=20, null=True)
    name = CharField(max_length=50, null=True)
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
    db.create_tables([Color],safe=True)