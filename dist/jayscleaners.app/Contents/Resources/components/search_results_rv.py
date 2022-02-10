from kivy.properties import ObjectProperty
from kivy.uix.recycleview import RecycleView
from models.sessions import sessions


class SearchResultsRV(RecycleView):
    rv_layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SearchResultsRV, self).__init__(**kwargs)

    def make_data(self, *args, **kwargs):
        if sessions.get('_searchResults')['value'] is not False:
            self.data = [{
                'text': f"{x['id']} | [b]{x['last_name']}, {x['first_name']}[/b] {x['phone']} | {'test'} |"
            } for x in sessions.get('_searchResults')['value']]
            print(self.data)
        pass
