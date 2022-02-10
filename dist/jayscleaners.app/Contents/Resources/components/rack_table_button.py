from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from models.sessions import sessions
from pubsub import pub

class RackTableButton(RecycleDataViewBehavior, Button):
    """ Add selection support to the Label """
    index = None
    id = None
    column = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        self.id = data['invoice_id']
        self.column = data['column']
        if data:
            try:
                return super(RackTableButton, self).refresh_view_attrs(rv, index, data)
            except ValueError:
                pass

        return False

    def on_press(self):
        sessions.put('_invoiceId',value=self.id)
        pass

    def on_release(self):
        if self.column == 4:
            pub.sendMessage("remove_row", invoice_id=int(self.id))
        else:
            pub.sendMessage("edit_row", invoice_id=int(self.id))