from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout


class ElementImageCommentAuthor(MDBoxLayout):
    image = StringProperty()
    author = StringProperty()
    comment = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
