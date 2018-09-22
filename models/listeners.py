from pubsub import pub
from models.sessions import sessions
from classes.mainScreen import MainScreen


# callbacks
def close_initial_popup(popup):
    popup.dismiss()


# listeners
pub.subscribe(close_initial_popup, 'close_loading_popup')
