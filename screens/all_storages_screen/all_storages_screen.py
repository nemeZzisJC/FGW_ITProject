from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.app import App

class AllStoragesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_words_storage_click(self):
        root = App.get_running_app().root
        screen_manager = root.ids.storages_screen_manager
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'all_words_screen'
        root.ids.all_words_screen.ids.words_scroll_view.scroll_y = 1
        root.ids.all_words_screen.add_words_to_screen()
