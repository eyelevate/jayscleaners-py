from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from models.sessions import sessions
from pubsub import pub

class InventoryItemsButton(RecycleDataViewBehavior, Button):
    """ Add selection support to the Label """
    index = None
    id = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        self.id = data['item_id']
        if 'Image' in data:
            self.ids.item_image.source=data['Image']['source']
        if data:
            try:
                return super(InventoryItemsButton, self).refresh_view_attrs(rv, index, data)
            except ValueError:
                pass

        return False

    def on_press(self):
        sessions.put("_itemId", value=int(self.id))

    def on_release(self):
        pub.sendMessage("set_item", item_id=int(self.id))