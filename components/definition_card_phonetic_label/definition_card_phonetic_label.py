from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty


class DefinitionCardPhoneticLabel(MDLabel):
    phonetic = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'fonts/times'
        self.font_size = '18sp'
