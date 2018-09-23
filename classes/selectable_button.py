from kivy.uix.button import Button
from kivy.uix.recycleview.views import RecycleDataViewBehavior


class SelectableButton(RecycleDataViewBehavior, Button):
    """ Add selection support to the Label """
    index = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        return super(SelectableButton, self).refresh_view_attrs(rv, index, data)

    def on_press(self):
        print('pressed')

    def on_release(self):
        print('removed')