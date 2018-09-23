from kivy.uix.button import Button
from kivy.uix.recycleview.views import RecycleDataViewBehavior


class SelectableButton(RecycleDataViewBehavior, Button):
    """ Add selection support to the Label """
    index = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        if data:
            try:
                return super(SelectableButton, self).refresh_view_attrs(rv, index, data)
            except ValueError:
                pass

        return False

    def on_press(self):
        print(self.index)

    def on_release(self):
        print(self.index)