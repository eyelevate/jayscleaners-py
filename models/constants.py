class Constants:

    def __init__(self):
        pass

    staticmethod

    def colors(self, key):
        colors = {
            'black': [0, 0, 0, 1],
            'white': [1, 1, 1, 1],
            'lime_green': [0.20, 0.80, 0.20, 1],
            'red': [1, 0, 0, 1],
            'yellow': [1, 1, 0, 1]
        }

        return colors[key]