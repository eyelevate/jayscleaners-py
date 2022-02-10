from kivy.uix.button import Button
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from pubsub import pub
from models.sessions import sessions


class AdjustIndividualButton(RecycleDataViewBehavior, Button):
    """ Add selection support to the Label """
    id = None
    index = None
    type = None
    price = None
    row = 0
    column = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        self.id = int(data['item_id']) if 'item_id' in data else None
        self.type = int(data['type']) if 'type' in data else None
        self.price = float(data['price']) if 'price' in data else None
        self.row = data['row'] if 'row' in data else None
        self.column = data['column'] if 'column' in data else None
        if data:
            try:

                return super(AdjustIndividualButton, self).refresh_view_attrs(rv, index, data)
            except ValueError:
                pass

        return False

    def on_press(self):
        pass

    def on_release(self):

        if self.column == 5:
            pub.sendMessage("item_row_delete_selected", item_id=self.id, row=self.row)
        else:
            pub.sendMessage("item_row_adjusted_selected", type=self.type, price=self.price, row=self.row)
        pass
