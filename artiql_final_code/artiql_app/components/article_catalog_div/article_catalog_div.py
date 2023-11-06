from kivymd.uix.card import MDCard
from kivy.app import App
from kivy.properties import StringProperty


class ArticleCatalogDiv(MDCard):
    heading = StringProperty()
    image = StringProperty()
    source = StringProperty()
    date = StringProperty()
    author = StringProperty()
    comment = StringProperty()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.on_article_click()

    def on_article_click(self):
        root = App.get_running_app().root
        reading_screen = root.ids.reading_screen
        reading_screen.ids.actual_scroll_view.scroll_y = 1
        reading_screen.start_adding_elements(self.heading)
