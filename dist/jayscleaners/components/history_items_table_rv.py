from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior


class HistoryRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout):
    datalen = 0


    def set_data(self, value):
        self.datalen = len(value)
        if self.children:
            self.children[0].on_data_update_sel(self.datalen, len(value))
        self.data = value
