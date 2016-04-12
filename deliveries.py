from peewee import *

db = SqliteDatabase('db/deliveries.db')

class Delivery(Model):

    id = PrimaryKeyField()
    delivery_id = IntegerField(null=True)
    company_id = IntegerField()
    route_name = CharField(max_length=50, null=True)
    day = CharField(max_length=50, null=True)
    limit = CharField(max_length=11, null=True)
    start_time = CharField(max_length=25, null=True)
    end_time = CharField(max_length=25, null=True)
    zipcode = TextField(null=True)
    blackout = TextField(null=True)
    reward_points = IntegerField(null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)


    class Meta:
        database = db