from kivy.uix.button import Button
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from models.sessions import sessions
from pubsub import pub


class ItemsDetailTableButton(RecycleDataViewBehavior, Button):
    """ Add selection support to the Label """
    index = None
    id = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        self.id = data['item_id'] if 'item_id' in data else None
        if data:
            try:
                return super(ItemsDetailTableButton, self).refresh_view_attrs(rv, index, data)
            except ValueError:
                pass

        return False

    def on_press(self):
        print(self.id)

    def on_release(self):
        pass
        # pub.sendMessage('select_item', item_id=self.id)