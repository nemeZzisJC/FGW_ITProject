from kivy.uix.label import Label
from kivy.properties import NumericProperty

class HeightDeterminator(Label):
    text_height = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(texture_size=self._update_text_height)

    def _update_text_height(self, instance, size):
        self.text_height = size[1]
