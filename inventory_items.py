from peewee import *

db = SqliteDatabase('db/inventory_items.db')

class InventoryItem(Model):

    id = PrimaryKeyField()
    item_id = IntegerField(null=True)
    inventory_id = IntegerField(null=True)
    company_id = IntegerField(null=True)
    name = CharField(max_length=50, null=True)
    description = TextField(null=True)
    tags = IntegerField(null=True)
    quantity = IntegerField(null=True)
    ordered = CharField(null=True)
    price = DecimalField(max_digits=11,decimal_places=2)
    image  = CharField(max_length=150, null= True)
    status = IntegerField(null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(null=True)
    updated_at = DateTimeField(null=True)


    class Meta:
        database = db