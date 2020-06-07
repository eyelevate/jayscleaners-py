from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior


class SelectableRecycleGridLayoutDuplicate(FocusBehavior, LayoutSelectionBehavior,
                                RecycleGridLayout):
    """ Adds selection and focus behaviour to the view. """