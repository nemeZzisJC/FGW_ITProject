from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
from classes.word import Word


class Content(MDBoxLayout):
    definition_text = StringProperty()
    translation_text = StringProperty()
    word_text = StringProperty()

    def __init__(self, word:Word, **kwargs):
        print("SURPRISINGLY, HERE")
        self.word = word
        self.word_text = word.word
        self.definition_text = self.word.definition
        self.translation_text = self.word.translation
        super().__init__(**kwargs)
