from kivy.app import App
from kivy.properties import StringProperty, NumericProperty
from components.element_paragraph.element_paragraph import ElementParagraph
from components.height_determinator.height_determinator import HeightDeterminator


class H1Heading(ElementParagraph):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update_text(self, text):
        self.input_text = text
        text_height = self.determine_height(self.input_text)
        self.needed_height = text_height

    def determine_height(self, text):
        app = App.get_running_app()
        lb = HeightDeterminator(text=text, font_size=self.font_size, text_size=(app.get_window_width() * 0.9, None), font_name='fonts/Helvetica-Bold', line_height=(self.font_size + 7) / self.font_size)
        lb.texture_update()
        text_height = lb.text_height
        return text_height
