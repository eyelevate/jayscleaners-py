from kivy.uix.button import Button
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from models.sessions import sessions
from pubsub import pub

class ItemsTableButton(RecycleDataViewBehavior, Button):
    """ Add selection support to the Label """
    index = None
    id = None
    column = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        self.id = data['item_id'] if 'item_id' in data else None
        self.column = int(data['column']) if 'column' in data else None
        if data:
            try:
                return super(ItemsTableButton, self).refresh_view_attrs(rv, index, data)
            except ValueError:
                pass

        return False

    def on_press(self):
        print(self.id)

    def on_release(self):
        if self.column == 5:
            pub.sendMessage('remove_item_row', item_id=self.id)
        else:
            pub.sendMessage('select_item', item_id=self.id)