from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
import os
os.environ['KIVY_IMAGE'] = 'pil'


class ElementMainHeadingCommentImageWithComment(MDBoxLayout):
    source = StringProperty()
    heading_text = StringProperty()
    author = StringProperty()
    date = StringProperty()
    comment = StringProperty()
    image = StringProperty()
    image_source = StringProperty()
    image_comment = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.main_image_with_comment_heading_text.update_text(
            self.heading_text)
        self.ids.comment.update_text(self.comment)
