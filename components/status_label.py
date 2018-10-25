from kivy.metrics import dp, sp
from kivy.properties import BooleanProperty, Clock
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse
from models.constants import Constants
from kivy.core.window import Window

class StatusLabel(Label):
    ''' Add selection support to the Label '''

    status_color = Constants().colors(key='red')
    h = dp(25)
    w = dp(25)
    s = dp(100)
    def __init__(self, **kwargs):
        super(StatusLabel, self).__init__(**kwargs)
        self.canvas.clear()
        self.size = (self.w, self.h)
        self.size_hint = (None, None)

        Window.bind(on_resize=self.set_resize)
        Clock.schedule_once(lambda *args: self.set_resize(), 5)

    def canvas_set(self, status):
        self.canvas.clear()
        self.status_color = Constants().colors(key='lime_green') if status == 'connected' else Constants().colors(key='red')
        self.set_resize()

    def set_resize(self, *args, **kwargs):
        self.canvas.clear()
        self.pos_hint= {'center_x':0.5, 'center_y':0.5}
        with self.canvas:
            Color(rgba=self.status_color)
            Ellipse(size= self.size,
                    pos=self.pos,
                    angle_start=0,
                    angle_end=360)