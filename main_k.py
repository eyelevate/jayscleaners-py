#!/usr/local/python
# import json
import requests
import companies

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import FadeTransition
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.popup import Popup


class MainScreen(Screen):
    def update_info(self):
        info = "Last updated {}".format("today")
        return info

    def login(self):
        pass

    def logout(self):
        pass

    def update_database(self):
        company_id = 1
        company_api = "2063288158-1"
        url = 'http://74.207.240.88/admins/api/update'
        data = {"id": company_id, "api_token": company_api}
        r = requests.post(url, json={data})
        if (r.status_code == 200):
            return r
        else:
            pass

    def test_create(self):
        company = {
            'company_id': 1,
            'name': 'Jays Cleaners Montlake',
            'street': '2350 24th Ave E',
            'suite': 'A',
            'city': 'Seattle',
            'state': 'WA',
            'zipcode': '98112',
            'email': 'wondo@jayscleaners.com',
            'phone': '2063288158',
            'api_key': '2063288158-1',
        }

        if companies.add(company):
            popup = Popup(title='Company Registration',
                          content=Label(text='Successfully saved company!'),
                          size_hint=(None, None), size=(400, 400))
        else:
            popup = Popup(title='Company Registration',
                          content=Label(text='Company Registration Failed'),
                          size_hint=(None, None), size=(400, 400))
        popup.open()


class DeliveryScreen(Screen):
    pass


class DropoffScreen(Screen):
    pass


class ReportsScreen(Screen):
    pass


class LoginScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class ScreenManagement(ScreenManager):
    pass


presentation = Builder.load_file("kv/style.kv")


class MainApp(App):
    def build(self):
        # Instantiate logged in user data
        self.user = None
        self.company_id = None
        return presentation


if __name__ == "__main__":
    # Window.clearcolor = (1, 1, 1, 1)
    # Window.size = (1366, 768)
    # Window.fullscreen = True
    MainApp().run()
