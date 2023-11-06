from kivymd.uix.screen import MDScreen
from kivy.app import App


class AllStoragesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_words_storage_click(self):
        root = App.get_running_app().root
        screen_manager = root.ids.storages_screen_manager
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'all_words_screen'
        root.ids.all_words_screen.is_selection_active = False
        root.ids.all_words_screen.ids.words_scroll_view.scroll_y = 1
        root.ids.all_words_screen.add_words_to_screen()

    def on_flashcards_storage_click(self):
        root = App.get_running_app().root
        screen_manager = root.ids.storages_screen_manager
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'flashcard_folders_screen'
        root.ids.flashcard_folders_screen.is_selection_active = False
        root.ids.flashcard_folders_screen.ids.folders_and_elements_scroll_view.scroll_y = 1
        root.ids.flashcard_folders_screen.add_folders_to_screen(
            '00000000-0000-0000-0000-000000000000')
        root.ids.flashcard_folders_screen.add_elements_to_screen()

    def on_workouts_storage_click(self):
        root = App.get_running_app().root
        screen_manager = root.ids.storages_screen_manager
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'workout_folders_screen'
        root.ids.workout_folders_screen.is_selection_active = False
        root.ids.workout_folders_screen.ids.folders_and_elements_scroll_view.scroll_y = 1
        root.ids.workout_folders_screen.add_folders_to_screen(
            '00000000-0000-0000-0000-000000000000')
        root.ids.workout_folders_screen.add_elements_to_screen()
