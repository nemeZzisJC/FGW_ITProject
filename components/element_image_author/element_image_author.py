from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout


class ElementImageAuthor(MDBoxLayout):
    image = StringProperty()
    author = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
