from peewee import *

db = SqliteDatabase('db/schedules.db')

class Schedule(Model):

    id = PrimaryKeyField()
    schedule_id = IntegerField(null=True)
    company_id = IntegerField(null=True)
    pickup_delivery_id = IntegerField(null=True)
    pickup_date = DateTimeField(null=True)
    dropoff_delivery_id = IntegerField(null=True)
    dropoff_date = DateTimeField(null=True)
    special_instructions = TextField(null=True)
    type = CharField(max_length=20,null=True)
    token = CharField(max_length=8, null=True)
    status = IntegerField(null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)


    class Meta:
        database = db

def initialize():
    """Create the database and the table if they do not exist"""
    db.connect()
    db.create_tables([Schedule],safe=True)