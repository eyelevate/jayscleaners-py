from peewee import *

db = SqliteDatabase('db/inventories.db')

class Inventory(Model):

    id = PrimaryKeyField()
    inventory_id = IntegerField(null=True)
    company_id = IntegerField(null=True)
    name = CharField(max_length=50, null=True)
    description = TextField(null=True)
    ordered = IntegerField(null=True)
    status = IntegerField(null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)


    class Meta:
        database = db