import webbrowser

from kivy.uix.screenmanager import Screen


class SettingsScreen(Screen):
    def accounts_page(self):
        webbrowser.open("https://www.jayscleaners.com/accounts")

    pass

    def inventories_page(self):
        webbrowser.open("https://www.jayscleaners.com/inventories")

    pass