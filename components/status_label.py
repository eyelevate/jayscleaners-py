from kivy.metrics import dp, sp
from kivy.properties import BooleanProperty
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse
from models.constants import Constants
from kivy.core.window import Window

class StatusLabel(Label):
    ''' Add selection support to the Label '''

    status_color = Constants().colors(key='red')

    def __init__(self, **kwargs):
        super(StatusLabel, self).__init__(**kwargs)
        Window.bind(on_resize=self.set_resize)

    def canvas_set(self, status):
        self.status_color = Constants().colors(key='lime_green') if status == 'connected' else Constants().colors(key='red')
        self.set_resize()

    def set_resize(self, *args, **kwargs):
        self.canvas.clear()
        with self.canvas:
            Color(rgba=self.status_color)
            Ellipse(size= (dp(25), dp(25)),
                    pos= [self.center_x - dp(25)/2, self.center_y - dp(25)/2],
                    angle_start=0,
                    angle_end=360)