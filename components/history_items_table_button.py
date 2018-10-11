from kivy.uix.button import Button
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from pubsub import pub
from models.sessions import sessions


class HistoryItemsTableButton(RecycleDataViewBehavior, Button):
    """ Add selection support to the Label """
    index = None
    id = None
    column = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        self.id = data['invoice_id'] if 'invoice_id' in data else None
        self.column = int(data['column']) if 'column' in data else None
        if data:
            try:
                return super(HistoryItemsTableButton, self).refresh_view_attrs(rv, index, data)
            except ValueError:
                pass

        return False

    def on_press(self):
        sessions.put('_invoiceId',value=self.id)

    def on_release(self):
        pub.sendMessage("select_invoice", invoice_id=int(self.id))
        pass
