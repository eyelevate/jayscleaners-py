import sys

from kivy.lang import Builder
from kivy.uix.popup import Popup
from models.kv_generator import KvString

KV = KvString()
class Popups:
    @staticmethod
    def dialog_msg(title_string, msg_string):
        popup = Popup()
        popup.title = title_string
        popup.size_hint = None, None
        popup.size = 800, 600
        body = KV.popup_alert(msg=msg_string)
        popup.content = Builder.load_string(body)
        popup.open()
        # Beep Sound
        sys.stdout.write('\a')
        sys.stdout.flush()

    @staticmethod
    def modal_msg(title_string, msg_string):
        popup = Popup()
        popup.title = title_string
        popup.size_hint = None, None
        popup.size = 800, 600
        body = KV.popup_alert(msg=msg_string)
        popup.content = Builder.load_string(body)
        popup.open()