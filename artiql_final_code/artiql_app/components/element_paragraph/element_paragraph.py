from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from components.height_determinator.height_determinator import HeightDeterminator
from kivy.app import App


class ElementParagraph(TextInput):
    input_text = StringProperty()
    needed_height = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root_el = App.get_running_app().root
        self.reading_screen = root_el.ids.reading_screen
        text_height = self.determine_height(self.input_text)
        self.needed_height = text_height

    def update_text(self, new_text):
        self.input_text = new_text
        text_height = self.determine_height(new_text)
        self.needed_height = text_height

    def determine_height(self, new_text):
        app = App.get_running_app()
        lbl = HeightDeterminator(
            text=new_text,
            font_name='fonts/Helvetica',
            line_height=1.35,
            font_size=20,
            text_size=(
                app.get_window_width() *
                0.9,
                None),
            size_hint_y=None,
            height=150,
            padding=[
                0,
                0,
                6,
                0])
        lbl.texture_update()
        lbl.height = lbl.texture_size[1]
        text_height = lbl.height
        return text_height

    def on_double_tap(self):
        pass

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        if self.selection_text:
            s_from = self.selection_from
            s_to = self.selection_to
            if s_from > s_to:
                start = s_to
                end = s_from - 1
            else:
                start = s_from
                end = s_to - 1

            pre_start = max(0, start - 1)
            after_end = min(end + 1, len(self.text) - 1)

            if (pre_start == 0 or self.text[pre_start] == ' ') and (
                    after_end == len(self.text) - 1 or self.text[after_end] == ' '):
                self.focus = False
                return

            # would need to write my own rfind that would find first non letter
            new_start_pos = self.text[:start + 1].rfind(' ')
            new_end_pos = self.text[end:].find(' ')

            if new_start_pos == -1:
                start = 0
            else:
                start = new_start_pos + 1

            for i in range(start, end + 1):
                if not self.text[i].isalpha():
                    start += 1
                elif self.text[i].isalpha():
                    break

            if new_end_pos == -1:
                end = len(self.text) - 2
            else:
                end += new_end_pos - 1

            for i in range(end, start - 1, -1):
                if not self.text[end].isalpha():
                    end -= 1
                elif self.text[end].isalpha():
                    break

            Clock.schedule_once(lambda x: self.select_text(start, end + 1))

            if any(i.isalpha() for i in self.text[start:end + 1]):
                self.reading_screen.slide_translation_card_up(
                    self.text[start:end + 1], self)
            else:
                self.focus = False
