class KvString:
    def table(self, id=False, rows=False, columns=False, row_height=False):
        table = '''
GridLayout:
    id: {id}
    cols: {columns}
'''.format(id=id, columns=columns)
        if row_height:
            table += '''
    row_force_default: True
    row_default_height:{row_height}
'''.format(row_height=row_height)
        if rows:
            table += '''
    rows: {rows}
'''.format(rows=rows)
        return table

    def table_th(self, text, rgba=(1, 1, 1, 1), text_color='000000'):
        return '''
    Label:
        size_hint_y: None
        font_size:'15sp'
        markup: True
        text: "[color=000000][b]{text}[/b][/color]"
        canvas.before:
            Color:
                rgba: {rgba}
            Rectangle:
                pos: self.pos
                size: self.size
'''.format(text=text, rgba=rgba, text_color=text_color)

    def table_tr(self, type=False, text=False, rgba=False, text_color=False):
        tr = '''
    {type}:
        size_hint_y:None
'''.format(type=type)

        if rgba:
            tr += '''
        canvas.before:
            Color:
                rgba: {rgba}
            Rectangle:
                pos: self.pos
                size: self.size
'''.format(rgba=rgba)
        if text_color:
            tr += '''
        markup: True
        text: [color={text_color}]{text}[/color]
'''.format(text_color=text_color, text=text)
        else:
            tr += '''
        text: {text}
'''.format(text=text)
        return tr

    def popup_root(self, body, footer):
        root = '''
BoxLayout:
    orientation: 'vertical'
    {content}
    {base}
'''.format(content=body, base=footer)
        return root

    def popup_body(self, layout, data, rows=False, columns=False, row_height=False):
        content = '''
    {layout}:
        size_hint: 1,0.9
'''.format(layout=layout)
        if rows:
            content += '''
        rows:{rows}
'''.format(rows=rows)
        if columns:
            content += '''
        cols: {columns}
'''.format(columns=columns)
        if row_height:
            content += '''
        row_force_default: True
        row_default_height:{row_height}
'''.format(row_height=row_height)
        if data:
            content +='''
        {data}
'''.format(data=data)
        return content

    def popup_footer(self, data):
        base = '''
    BoxLayout:
        size_hint: 1,0.1
        {content}
'''.format(content=data)
        return base

    def popup_cancel_button(self):
        return '''
        Button:
            size_hint_y:None
            font_size:'15sp'
            markup: True
            text: 'Cancel'
            on_press: root.parent.parent.parent.dismiss()
'''

    def popup_item(self, type, data, text_color=False, bold=False, italic=False, rgba=False, callback=False):
        item = '''
        {type}:
            size_hint_y:None
            markup: True
'''.format(type=type)
        text_string = ''
        if text_color:
            text_string += '[color={}]'.format(str(text_color))
        if bold:
            text_string += '[b]'
        if italic:
            text_string += '[i]'

        text_string += '{text}'.format(text=data)

        if text_color:
            text_string += '[/color]'
        if bold:
            text_string += '[/b]'
        if italic:
            text_string += '[/i]'
        item += '''
            text:"{text_string}"
'''.format(text_string=text_string, callback=callback)
        if rgba:
            item += '''
            canvas.before:
                Color:
                    rgba: {rgba}
                Rectangle:
                    pos: self.pos
                    size: self.size
'''.format(rgba=rgba)
        if callback:
            item += '''
            on_release:{callback}
'''.format(callback=callback)

        return item

    def popup_alert(self,msg):
        return '''
BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        size_hint: 1,0.8
        Label:
            text:"{text}"
    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1,0.2
        Button:
            font_size:'15sp'
            markup: True
            text: 'Okay'
            on_press: root.parent.parent.parent.dismiss()'''.format(text=msg)

    def popup_confirm(self, msg=False,on_confirm=False,on_cancel=False):
        return '''
BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        size_hint: 1,0.8
        Label:
            markup:True
            text:"{text}"
    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1,0.2
        Button:
            font_size:'15sp'
            markup: True
            text: 'Cancel'
            on_release: {cancel}
        Button:
            font_size:'15sp'
            markup: True
            text: 'Okay'
            on_release: {confirm}'''.format(text=msg,cancel=on_cancel,confirm=on_confirm)

    def widget_item(self, type, data, text_color=False, bold=False, italic=False,
                    rgba=False, background_rgba=False, callback=False):
        item = '''
{type}:
    size_hint_y:None
    font_size:'15sp'
    markup: True
'''.format(type=type)
        text_string = ''
        if text_color:
            text_string += '[color={}]'.format(str(text_color))
        if bold:
            text_string += '[b]'
        if italic:
            text_string += '[i]'

        text_string += '{text}'.format(text=data)

        if text_color:
            text_string += '[/color]'
        if bold:
            text_string += '[/b]'
        if italic:
            text_string += '[/i]'
        item += '''
    text:"{text_string}"
'''.format(text_string=text_string, callback=callback)
        if background_rgba:
            item += '''
    background_color: {}'''.format(background_rgba)
        if rgba:
            item += '''
    canvas.before:
        Color:
            rgba: {rgba}
        Rectangle:
            pos: self.pos
            size: self.size
'''.format(rgba=rgba)
        if callback:
            item += '''
    on_release:{callback}
'''.format(callback=callback)

        return item

    def invoice_tr(self,state, data, selected = False, invoice_id=False,
                   callback=False, spinner = False, spinner_text = False,
                   text_wrap = False):
        if state == 0:  # header
            tr = '''
Label:
    size_hint_y: None
    markup: True
    text: "[color=000000][b]{text}[/b][/color]"
    font_size:'15sp'
    {txt_wrap}
    valign:"{valign}"
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size'''.format(text=data,
                                      txt_wrap='text_size: self.size' if text_wrap else '',
                                      valign='top' if text_wrap else 'middle')
            return tr
        elif state == 6:  # Quick Drop
            background_rgba = '0.98431373,1,0,0.1' if selected else '0.9960784314,1,0.7176470588,0.1'
            background_color = '0.98431373,1,0,1' if selected else '0.9960784314,1,0.7176470588, 1'
            text_color = '000000' if selected else '000000'
        elif state == 5:  # paid and done
            background_rgba = '0.369,0.369,0.369,0.1' if selected else '0.826, 0.826, 0.826, 0.1'
            background_color = '0.369,0.369,0.369,1' if selected else '0.826, 0.826, 0.826, 1'
            text_color = 'e5e5e5' if selected else '000000'
        elif state == 4:  # Quick Drop | prepaid | Gone np
            background_rgba = '1,0,0,0.1' if selected else '1, 0.717, 0.717, 0.1'
            background_color = '1,0,0,1' if selected else '1, 0.717, 0.717, 1'
            text_color = 'ffcccc' if selected else 'ff0000'
        elif state == 3:  # Racked and Ready
            background_rgba = '0,0.64,0.149,0.1' if selected else '0.847,0.968,0.847,0.1'
            background_color = '0,0.64,0.149,1' if selected else '0.847,0.968,0.847,1'
            text_color = 'D8F7D8' if selected else '00A326'
        elif state == 2:  # Overdue
            background_rgba = '0.059,0.278,1,0.1' if selected else '0.816, 0.847, 0.961, 0.1'
            background_color = '0.059,0.278,1,1' if selected else '0.816, 0.847, 0.961, 1'
            text_color = 'D0D8F5' if selected else '0F47FF'
        else:  # Not ready yet
            background_rgba = '0.369,0.369,0.369,0.1' if selected else '0.826, 0.826, 0.826, 0.1'
            background_color = '0.369,0.369,0.369,1' if selected else '0.826, 0.826, 0.826, 1'
            text_color = 'e5e5e5' if selected else '000000'

        if spinner:
            default_text = '{} {}'.format(len(data) if data else 0,spinner_text)
            data_string = ''
            if data:
                for item_name in data:
                    data_string += '"{}",'.format(item_name)
            if len(data) > 0:
                tr = '''
Spinner:
    text: '{title}'
    {txt_wrap}
    valign:"{valign}"
    values: "{colors}"'''.format(title = default_text,
                               colors='({})'.format(data_string),
                               txt_wrap='text_size: self.size' if text_wrap else '',
                               valign='top' if text_wrap else 'middle')
            else:
                tr = '''
Button:
    size_hint_y: None
    markup: True
    font_size:'15sp'
    text: "[color={text_color}]{text}[/color]"
    background_color:[{background_rgba}]
    on_release: {cb}
    {txt_wrap}
    valign: "{valign)"
    canvas.before:
        Color:
            rgba: {background_color}
        Rectangle:
            pos: self.pos
            size: self.size'''.format(text=default_text,
                                      txt_wrap = 'text_size: self.size' if text_wrap else '',
                                      valign = 'top' if text_wrap else 'middle',
                                      background_rgba=background_rgba,
                                      background_color=background_color,
                                      text_color=text_color,
                                      inv_id= invoice_id,
                                      cb= callback)
        else:
            tr = '''
Button:
    size_hint_y: None
    markup: True
    font_size:'15sp'
    text: "[color={text_color}]{text}[/color]"
    background_color:[{background_rgba}]
    on_release: {cb}
    {txt_wrap}
    valign: "{valign}"
    canvas.before:
        Color:
            rgba: {background_color}
        Rectangle:
            pos: self.pos
            size: self.size'''.format(text=data,
                                      txt_wrap='text_size:self.size' if text_wrap else '',
                                      valign='top' if text_wrap else 'middle',
                                      background_rgba=background_rgba,
                                      background_color=background_color,
                                      text_color=text_color,
                                      inv_id= invoice_id,
                                      cb= callback)
        return tr

    def sized_invoice_tr(self,
                         state,
                         data,
                         size_hint_x: False,
                         selected=False,
                         invoice_id=False,
                         on_press=False,
                         on_release=False,
                         spinner=False,
                         spinner_text=False,
                         text_wrap=False):
        if state == 0:  # header
            tr = '''
Label:
    size_hint_x: {hint_x}
    size_hint_y: None
    markup: True
    text: "[color=000000][b]{text}[/b][/color]"
    font_size:'15sp'
    text_size: self.size
    halign: 'center'
    valign: 'middle'
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size'''.format(hint_x=size_hint_x,
                                      text=data,
                                      txt_wrap='text_size: self.size' if text_wrap else '',
                                      valign='top' if text_wrap else 'middle')
            return tr
        elif state == 6:  # Quick Drop
            background_rgba = '0.98431373,1,0,0.1' if selected else '0.9960784314,1,0.7176470588,0.1'
            background_color = '0.98431373,1,0,1' if selected else '0.9960784314,1,0.7176470588, 1'
            text_color = '000000' if selected else '000000'
        elif state == 5:  # paid and done
            background_rgba = '0.369,0.369,0.369,0.1' if selected else '0.826, 0.826, 0.826, 0.1'
            background_color = '0.369,0.369,0.369,1' if selected else '0.826, 0.826, 0.826, 1'
            text_color = 'e5e5e5' if selected else '000000'
        elif state == 4:  # Quick Drop | prepaid | Gone np
            background_rgba = '1,0,0,0.1' if selected else '1, 0.717, 0.717, 0.1'
            background_color = '1,0,0,1' if selected else '1, 0.717, 0.717, 1'
            text_color = 'ffcccc' if selected else 'ff0000'
        elif state == 3:  # Racked and Ready
            background_rgba = '0,0.64,0.149,0.1' if selected else '0.847,0.968,0.847,0.1'
            background_color = '0,0.64,0.149,1' if selected else '0.847,0.968,0.847,1'
            text_color = 'D8F7D8' if selected else '00A326'
        elif state == 2:  # Overdue
            background_rgba = '0.059,0.278,1,0.1' if selected else '0.816, 0.847, 0.961, 0.1'
            background_color = '0.059,0.278,1,1' if selected else '0.816, 0.847, 0.961, 1'
            text_color = 'D0D8F5' if selected else '0F47FF'
        else:  # Not ready yet
            background_rgba = '0.369,0.369,0.369,0.1' if selected else '0.826, 0.826, 0.826, 0.1'
            background_color = '0.369,0.369,0.369,1' if selected else '0.826, 0.826, 0.826, 1'
            text_color = 'e5e5e5' if selected else '000000'
        if spinner:
            default_text = '{} {}'.format(len(data) if data else 0, spinner_text)
            data_string = ''
            if data:
                for item_name in data:
                    data_string += '"{}",'.format(item_name)
            if len(data) > 0:
                tr = '''
Spinner:
    size_hint_x: {hint_x}
    text: '{title}'
    {txt_wrap}
    valign:"{valign}"
    values: "{colors}"'''.format(size_hint_x= size_hint_x,
                                 title=default_text,
                                 colors='({})'.format(data_string),
                                 txt_wrap='text_size: self.size' if text_wrap else '',
                                 valign='top' if text_wrap else 'middle')
            else:
                tr = '''
Button:
    size_hint_x: {hint_x}
    size_hint_y: None
    markup: True
    font_size:'15sp'
    text: "[color={text_color}]{text}[/color]"
    background_color:[{background_rgba}]
    on_press: {opress}
    on_release: {orelease}
    {txt_wrap}
    valign: "{valign)"
    canvas.before:
        Color:
            rgba: {background_color}
        Rectangle:
            pos: self.pos
            size: self.size'''.format(hint_x=size_hint_x,
                                      text=default_text,
                                      txt_wrap='text_size: self.size' if text_wrap else '',
                                      valign='top' if text_wrap else 'middle',
                                      background_rgba=background_rgba,
                                      background_color=background_color,
                                      text_color=text_color,
                                      inv_id=invoice_id,
                                      opress=on_press,
                                      orelease=on_release)
        else:
            tr = '''
Button:
    size_hint_x: {hint_x}
    size_hint_y: None
    markup: True
    font_size:'15sp'
    text: "[color={text_color}]{text}[/color]"
    background_color:[{background_rgba}]
    on_press: {opress}
    on_release: {orelease}
    {txt_wrap}
    valign: "{valign}"
    canvas.before:
        Color:
            rgba: {background_color}
        Rectangle:
            pos: self.pos
            size: self.size'''.format(hint_x= size_hint_x,
                                      text=data,
                                      txt_wrap='text_size:self.size' if text_wrap else '',
                                      valign='top' if text_wrap else 'middle',
                                      background_rgba=background_rgba,
                                      background_color=background_color,
                                      text_color=text_color,
                                      inv_id=invoice_id,
                                      opress=on_press,
                                      orelease=on_release)
        return tr

    def inventory_items_panel(self, inventories):
        panel = '''
TabbedPanel:
    id: tabbedPanel
    do_default_tab: False
    size_hint: 1,1'''
        for inventory in inventories:
            inventory_id = inventory['id']
            inventory_name = inventory['name']
            inventory_items = inventory['inventory_items']
            panel += '''
    InventoryItemsButton:
        markup: True
        disabled: False
        size_hint: 1, None
        text_size: self.size
        valign: 'bottom'
        halign: 'center'
        font_size:sp(17)
        canvas.before:
            Color:
                rgba: (0.0, 0.9, 0.1, 0.3)
            Rectangle:
                pos: self.pos
                size: self.size
    RecycleView: 
        viewclass: 'InventoryItemsButton'
        SelectableRecycleBoxLayout:
            id: tab_content_{}
            bar_width: dp(5)
            default_size: None, sp(150)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'horizontal'
            multiselect: False
            touch_multiselect: False
    TabbedPanelHeader:
            id: def_tab
            text: '{}'
            content:tab_content_{}.__self__
    '''.format(inventory_id, inventory_name, inventory_id)


        return panel
