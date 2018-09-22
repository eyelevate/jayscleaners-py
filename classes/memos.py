from kivy.factory import Factory
from kivy.properties import ObjectProperty, partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from models.sessions import sessions

from classes.popups import Popups
from models.memos import Memo


class MemosScreen(Screen):
    popup_memo = Popup()
    memo_id = None
    memos_table = ObjectProperty(None)
    reorder_start_id = None
    reorder_end_id = None
    msg = None

    def reset(self):
        # Pause Schedule
        #
        self.memo_id = None
        self.create_memo_table()
        pass

    def create_memo_table(self):
        self.memos_table.clear_widgets()
        mmos = Memo()
        memos = mmos.where({'company_id': sessions.get('_companyId')['value'],
                            'ORDER_BY': 'ordered asc'})
        if memos:
            for memo in memos:
                m_id = memo['id']
                memo_msg = memo['memo']
                if self.reorder_start_id is None:
                    memo_item = Factory.LongButton(text='{}'.format(memo_msg),
                                                   on_press=partial(self.set_memo_id, m_id),
                                                   on_release=self.memo_actions_popup)
                elif self.reorder_start_id is m_id:
                    memo_item = Factory.LongButton(text='{}'.format(memo_msg),
                                                   markup=True,
                                                   on_press=partial(self.set_memo_id, m_id),
                                                   on_release=self.memo_actions_popup,
                                                   background_normal='',
                                                   background_color=(0, 0.64, 0.149, 1))
                elif self.reorder_start_id != None and self.reorder_start_id != m_id:
                    memo_item = Factory.LongButton(text='{}'.format(memo_msg),
                                                   on_press=partial(self.set_reorder_end_id, m_id))

                self.memos_table.add_widget(memo_item)

    def memo_actions_popup(self, *args, **kwargs):
        popup = Popup()
        popup.title = 'Memo Actions'
        popup.size_hint = (None, None)
        popup.size = (800, 600)
        content = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.9))
        inner_layout_1.add_widget(Button(text='reorder',
                                         on_press=self.reorder_start,
                                         on_release=popup.dismiss))
        inner_layout_1.add_widget(Button(text='edit',
                                         on_press=popup.dismiss,
                                         on_release=self.popup_memos_edit))
        inner_layout_1.add_widget(Button(text='delete',
                                         on_press=self.delete_confirm))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='cancel',
                                         on_press=popup.dismiss))
        content.add_widget(inner_layout_1)
        content.add_widget(inner_layout_2)
        popup.content = content
        popup.open()

    def set_memo_id(self, id, *args, **kwargs):
        self.memo_id = id

    def reorder_start(self, *args, **kwargs):
        self.reorder_start_id = self.memo_id
        self.reset()

    def set_reorder_end_id(self, id, *args, **kwargs):
        print('end set')
        self.reorder_end_id = id
        self.reorder()

    def reorder(self, *args, **kwargs):
        mmos = Memo()
        memo_start = mmos.where({'id': self.reorder_start_id})
        order_start = None
        if memo_start:
            for memo in memo_start:
                order_start = memo['ordered']
        memo_end = mmos.where({'id': self.reorder_end_id})
        order_end = None
        if memo_end:
            for memo in memo_end:
                order_end = memo['ordered']

        put_start = mmos.put(where={'id': self.reorder_start_id},
                             data={'ordered': order_end})

        put_end = mmos.put(where={'id': self.reorder_end_id},
                           data={'ordered': order_start})
        if put_start and put_end:
            self.reorder_start_id = None
            self.reorder_end_id = None
            self.reset()

        else:
            Popups.modal_msg('Reorder Status', 'Could not reorder. Try again.')

        pass

    def popup_memos_add(self):
        self.popup_memo.title = 'Add A Memo'
        content = BoxLayout(orientation='vertical')
        inner_layout_1 = GridLayout(cols=2,
                                    size_hint=(1, 0.9),
                                    row_force_default=True,
                                    row_default_height='50sp')
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Memo'))
        self.msg = Factory.CenterVerticalTextInput()
        inner_layout_1.add_widget(self.msg)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='cancel',
                                         on_press=self.popup_memo.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=00ff00][b]Add[/b][/color]',
                                         on_press=self.add_memo))
        content.add_widget(inner_layout_1)
        content.add_widget(inner_layout_2)
        self.popup_memo.content = content
        self.popup_memo.open()

    def add_memo(self, *args, **kwargs):
        mmos = Memo()
        search = mmos.where({'company_id': sessions.get('_companyId')['value'],
                             'ORDER_BY': 'ordered desc',
                             'LIMIT': 1})
        next_ordered = 1
        if search:
            for memo in search:
                next_ordered = int(memo['ordered']) + 1

        if self.msg.text is not None:
            mmos.company_id = sessions.get('_companyId')['value']
            mmos.memo = self.msg.text
            mmos.ordered = next_ordered
            mmos.status = 1

            if mmos.add():
                Popups.modal_msg('Memo', 'Successfully added new memo')

                self.popup_memo.dismiss()
                self.memo_id = None
                self.reorder_start_id = None
                self.reorder_end_id = None
                self.reset()

    def delete_confirm(self, *args, **kwargs):
        popup = Popup()
        popup.title = 'Delete Confirmation'
        layout = BoxLayout(orientation='vertical')
        inner_layout_1 = BoxLayout(orientation='vertical',
                                   size_hint=(1, 0.9))
        inner_layout_1.add_widget(Label(text='Are you sure?'))
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='cancel',
                                         on_press=popup.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=00ff00][b]cancel[/b][/color]',
                                         on_press=popup.dismiss,
                                         on_release=self.delete_memo))
        popup.content = layout
        popup.open()

    def delete_memo(self, *args, **kwargs):
        mmos = Memo()
        mmos.id = self.memo_id
        if mmos.delete():
            Popups.modal_msg('Deleted Memo', 'Successfully removed memo')
            self.reset()

    def popup_memos_edit(self, *args, **kwargs):

        mmos = Memo()
        memos = mmos.where({'id': self.memo_id})
        msg = ''
        if memos:
            for memo in memos:
                msg = memo['memo']
        self.popup_memo.title = 'Edit Memo'
        content = BoxLayout(orientation='vertical')
        inner_layout_1 = GridLayout(cols=2,
                                    size_hint=(1, 0.9),
                                    row_force_default=True,
                                    row_default_height='50sp')
        inner_layout_1.add_widget(Factory.CenteredFormLabel(text='Memo'))
        self.msg = Factory.CenterVerticalTextInput(text=str(msg))
        inner_layout_1.add_widget(self.msg)
        inner_layout_2 = BoxLayout(orientation='horizontal',
                                   size_hint=(1, 0.1))
        inner_layout_2.add_widget(Button(text='cancel',
                                         on_press=self.popup_memo.dismiss))
        inner_layout_2.add_widget(Button(markup=True,
                                         text='[color=00ff00][b]Edit[/b][/color]',
                                         on_press=self.edit_memo))
        content.add_widget(inner_layout_1)
        content.add_widget(inner_layout_2)
        self.popup_memo.content = content
        self.popup_memo.open()

    def edit_memo(self, *args, **kwargs):
        mmos = Memo()
        mmos.memo = self.msg.text
        put = mmos.put(where={'id': self.memo_id},
                       data={'memo': self.msg.text})
        if put:
            Popups.modal_msg('Updated Memo', 'Successfully updated memo')

            self.popup_memo.dismiss()
            self.reset()
            self.memo_id = None
            self.reorder_start_id = None
            self.reorder_end_id = None
        else:
            Popups.modal_msg('Update Memo Error', 'Could not edit memo. Please try again.')