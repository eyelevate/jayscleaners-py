from kivy.uix.button import Button
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from pubsub import pub
from models.sessions import sessions
from kivy.uix.screenmanager import ScreenManager


class HistoryInvoiceItemsTableButton(RecycleDataViewBehavior, Button):
    """ Add selection support to the Label """
    index = None
    id = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        self.id = int(data['id']) if 'id' in data else None
        if data:
            try:
                return super(HistoryInvoiceItemsTableButton, self).refresh_view_attrs(rv, index, data)
            except ValueError:
                pass

        return False

    def on_press(self):
        sessions.put('_itemId',value=self.id)

    def on_release(self):
        pub.sendMessage("app_change_screen", screen='item_details')

        pass
