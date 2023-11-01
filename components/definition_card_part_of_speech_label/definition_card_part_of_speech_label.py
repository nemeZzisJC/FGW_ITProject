from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty

class DefinitionCardPartOfSpeechLabel(MDLabel):
    part_of_speech = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'fonts/Helvetica-bold'
        self.font_size = '17sp'
