from kivy.factory import Factory
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from classes.popups import *
from models.colors import Colored
from models.sessions import sessions
from models.static import Static

class ColorsScreen(Screen):
    select_color = ObjectProperty(None)
    colors_table = ObjectProperty(None)
    add_popup = Popup()
    color_name = ObjectProperty(None)
    color_hex = None
    color_id = None
    color_rgba = StringProperty(None)
    reorder_start_id = False
    reorder_end_id = False

    def reset(self):
        # Pause Schedule
        #
        self.set_color_table()
        self.color_hex = ''
        self.color_id = ''
        self.reorder_end_id = False

    pass

    def set_color_table(self):
        self.colors_table.clear_widgets()

        colored = Colored()
        colorings = colored.where({'company_id': sessions.get('_companyId')['value'], 'ORDER_BY': 'ordered asc'})

        if colorings:
            for clr in colorings:
                if self.reorder_start_id and clr['color_id'] == self.reorder_start_id:
                    c1 = '''
Button:
    font_size:'17sp'
    markup:True
    text: '[b]{color_name}[/b]'
    disabled: False
    text_size:self.size
    valign:'bottom'
    halign:'center'
    on_release: root.parent.parent.parent.parent.parent.action_popup({color_id})
    background_normal: ''
    background_color: {background_rgba}
    Label:
        id: color_label
        size: '50sp','50sp'
        center_x: self.parent.center_x
        center_y: self.parent.center_y + sp(20)
        canvas.before:
            Color:
                rgba: {color_rgba}
            Rectangle:
                pos: self.pos
                size: self.size
'''.format(color_name=clr['name'],
           color_id=clr['color_id'],
           background_rgba=(0, 0.64, 0.149, 1),
           color_rgba=Static.color_rgba(clr['color']))
                elif self.reorder_start_id and clr['color_id'] != self.reorder_start_id:
                    c1 = '''
Button:
    font_size:'17sp'
    markup:True
    text: '[b]{color_name}[/b]'
    disabled: False
    text_size:self.size
    valign:'bottom'
    halign:'center'
    on_release: root.parent.parent.parent.parent.parent.change_order({color_id})
    Label:
        id: color_label
        size: '50sp','50sp'
        center_x: self.parent.center_x
        center_y: self.parent.center_y + sp(20)
        canvas.before:
            Color:
                rgba: {color_rgba}
            Rectangle:
                pos: self.pos
                size: self.size
'''.format(color_name=clr['name'],
           color_id=clr['color_id'],
           color_rgba=Static.color_rgba(clr['color']))
                else:
                    c1 = '''
Button:
    font_size:'17sp'
    markup:True
    text: '[b]{color_name}[/b]'
    disabled: False
    text_size:self.size
    valign:'bottom'
    halign:'center'
    on_release: root.parent.parent.parent.parent.parent.action_popup({color_id})
    Label:
        id: color_label
        size: '50sp','50sp'
        center_x: self.parent.center_x
        center_y: self.parent.center_y + sp(20)
        canvas.before:
            Color:
                rgba: {color_rgba}
            Rectangle:
                pos: self.pos
                size: self.size
'''.format(color_name=clr['name'],
           color_id=clr['color_id'],
           color_rgba=Static.color_rgba(clr['color']))

                self.colors_table.add_widget(Builder.load_string(c1))

    def change_order(self, color_id, *args, **kwargs):
        self.reorder_end_id = color_id
        swap_order = {self.reorder_start_id: '', self.reorder_end_id: ''}
        coloreds = Colored()
        start_colors = coloreds.where({'color_id': self.reorder_start_id, 'company_id': sessions.get('_companyId')['value']})
        if start_colors:
            for clr in start_colors:
                swap_order[self.reorder_end_id] = clr['ordered']

        end_colors = coloreds.where({'color_id': self.reorder_end_id, 'company_id': sessions.get('_companyId')['value']})
        if end_colors:
            for clr in end_colors:
                swap_order[self.reorder_start_id] = clr['ordered']
        if swap_order:
            for key, index in swap_order.items():
                coloreds.put(where={'color_id': key, 'company_id': sessions.get('_companyId')['value']},
                             data={'ordered': index})

        self.reorder_end_id = False
        self.reorder_start_id = False
        self.reset()

    def popup_add(self):
        self.add_popup.title = 'Add Color'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(size_hint=(1, 0.9),
                                   orientation='vertical')
        color_widget = ColorPicker()
        color_widget.bind(color=self.set_color)
        color_grid = GridLayout(size_hint_x=1,
                                size_hint_y=None,
                                cols=2,
                                rows=1,
                                row_force_default=True,
                                row_default_height='40sp',
                                padding=[10, 10, 10, 10])
        self.color_name = Factory.CenterVerticalTextInput()
        color_grid.add_widget(Factory.CenteredFormLabel(text='Color Name:'))
        color_grid.add_widget(self.color_name)
        inner_layout_1.add_widget(color_grid)
        inner_layout_1.add_widget(color_widget)

        inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                   orientation='horizontal')
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_release=self.add_popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=19ff52][b]Add[/b][/color]',
                                         on_release=self.add_color))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.add_popup.content = layout
        self.add_popup.open()

    def popup_edit(self, *args, **kwargs):
        coloreds = Colored()
        clrds = coloreds.where({'color_id': self.color_id, 'company_id': sessions.get('_companyId')['value']})
        color_name = ''
        color_hex = ''
        if clrds:
            for clr in clrds:
                color_name = clr['name']
                color_hex = clr['color']

        self.add_popup.title = 'Add Color'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(size_hint=(1, 0.9),
                                   orientation='vertical')
        color_widget = ColorPicker(hex_color=color_hex)
        color_widget.bind(color=self.set_color)
        color_grid = GridLayout(size_hint_x=1,
                                size_hint_y=None,
                                cols=2,
                                rows=1,
                                row_force_default=True,
                                row_default_height='40sp',
                                padding=[10, 10, 10, 10])
        self.color_name = Factory.CenterVerticalTextInput(text='{}'.format(color_name))
        color_grid.add_widget(Factory.CenteredFormLabel(text='Color Name:'))
        color_grid.add_widget(self.color_name)
        inner_layout_1.add_widget(color_grid)
        inner_layout_1.add_widget(color_widget)

        inner_layout_2 = BoxLayout(size_hint=(1, 0.1),
                                   orientation='horizontal')
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_release=self.add_popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=19ff52][b]Edit[/b][/color]',
                                         on_release=self.edit_color))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        self.add_popup.content = layout
        self.add_popup.open()

    def set_color(self, instance, *args, **kwargs):
        self.color_hex = instance.hex_color

    def add_color(self, *args, **kwargs):

        coloreds = Colored()
        # get new ordered number
        new_orders = coloreds.where({'company_id': sessions.get('_companyId')['value'], 'ORDER_BY': 'id desc', 'LIMIT': 1})
        new_order = 1
        if new_orders:
            for no in new_orders:
                ordered = no['ordered']
                new_order = ordered + 1
        coloreds.company_id = sessions.get('_companyId')['value']
        coloreds.color = self.color_hex
        coloreds.name = self.color_name.text
        coloreds.ordered = new_order
        coloreds.status = 1
        if coloreds.add():
            Popups.modal_msg('New Color', 'Succesfully added a new color.')
            self.add_popup.dismiss()

    def edit_color(self, *args, **kwargs):

        coloreds = Colored()
        # get new ordered number
        put = coloreds.put(where={'color_id': self.color_id, 'company_id': sessions.get('_companyId')['value']},
                           data={'color': self.color_hex,
                                 'name': self.color_name.text})

        if put:
            Popups.modal_msg('Edit Color', 'Succesfully edited color.')
            self.add_popup.dismiss()

    def action_popup(self, id, *args, **kwargs):
        self.color_id = id
        popup = Popup()
        popup.title = 'Edit Color'
        popup.size_hint = (None, None)
        popup.size = (800, 600)
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.7))
        inner_layout_1.add_widget(Button(text='Reorder',
                                         on_press=popup.dismiss,
                                         on_release=self.reorder_start))
        inner_layout_1.add_widget(Button(text='Edit',
                                         on_press=popup.dismiss,
                                         on_release=self.popup_edit))
        inner_layout_1.add_widget(Button(text='Delete',
                                         on_release=self.delete_confirm))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.3))
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_release=popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def reorder_start(self, *args, **kwargs):
        self.reorder_start_id = self.color_id
        self.reset()

    def delete_confirm(self, *args, **kwargs):
        print('here')
        popup = Popup()
        popup.size_hint = (None, None)
        popup.size = (800, 600)
        popup.title = 'Delete Confirmation'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = Label(size_hint=(1, 0.7),
                               markup=True,
                               text='Are you sure you wish to delete this Color (#{})?'.format(self.color_id))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.3))
        inner_layout_2.add_widget(Button(text='Cancel',
                                         on_release=popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=FF0000][b]Delete[/b][/color]',
                                         on_press=self.delete_item,
                                         on_release=popup.dismiss))
        layout.add_widget(inner_layout_1)
        layout.add_widget(inner_layout_2)
        popup.content = layout
        popup.open()

    def delete_item(self, *args, **kwargs):
        coloreds = Colored()
        deleted = coloreds.where({'company_id': sessions.get('_companyId')['value'],
                                  'color_id': self.color_id})
        if deleted:
            for deleted_color in deleted:
                coloreds.id = deleted_color['id']
                if coloreds.delete():
                    Popups.modal_msg('Deleted Color Notification', 'Successfully deleted color')

        else:
            Popups.modal_msg('Deleted Color Notification', 'Could not delete color. Try again.')

        self.reset()