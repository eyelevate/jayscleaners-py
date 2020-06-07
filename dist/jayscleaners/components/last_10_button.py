from kivy.uix.button import Button
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from models.sessions import sessions
from pubsub import pub

class Last10Button(RecycleDataViewBehavior, Button):
    """ Add selection support to the Label """
    index = None
    id = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        self.id = data['customer_id'] if 'customer_id' in data else None
        if data:
            try:
                return super(Last10Button, self).refresh_view_attrs(rv, index, data)
            except ValueError:
                pass

        return False

    def on_press(self):
        try:
            sessions.put('_customerId',value=self.id)
        except TypeError:
            pass


    def on_release(self):
        pub.sendMessage('customer_select', customer_id=self.id)