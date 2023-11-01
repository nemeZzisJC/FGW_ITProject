from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty, NumericProperty

class DefinitionCardDefinitionLabel(MDLabel):
    cnt = NumericProperty()
    definition_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'fonts/Helvetica'
