from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout


class ElementMainHeadingCommentImage(MDBoxLayout):
    source = StringProperty()
    heading_text = StringProperty()
    author = StringProperty()
    date = StringProperty()
    comment = StringProperty()
    image = StringProperty()
    image_source = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.main_heading_text.update_text(self.heading_text)
        self.ids.comment.update_text(self.comment)
