from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout


class ElementImageNoComment(MDBoxLayout):
    image = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
