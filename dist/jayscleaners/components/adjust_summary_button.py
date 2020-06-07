from kivy.uix.button import Button
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from pubsub import pub
from models.sessions import sessions


class AdjustSummaryButton(RecycleDataViewBehavior, Button):
    """ Add selection support to the Label """
    index = None
    type = None
    price = None
    row = 0

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        self.type = int(data['type']) if 'type' in data else None
        self.price = float(data['price']) if 'price' in data else None
        self.row = int(data['row']) if 'row' in data else 0
        if data:
            try:
                return super(AdjustSummaryButton, self).refresh_view_attrs(rv, index, data)
            except ValueError:
                pass

        return False

    def on_press(self):
        pass

    def on_release(self):
        pub.sendMessage("adjustment_calculator", type=self.type, price=self.price, row=self.row)
        pass
