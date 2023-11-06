from kivymd.uix.screen import MDScreen
from kivy.app import App
from classes.word import Word
from classes.word import WordAlreadySaved
from classes.word import WordWithoutTranslationDefinition
from components.dialog_okay_button.dialog_okay_button import DialogOkayButton
from components.success_snackbar.success_snackbar import SuccessSnackbar
from kivymd.uix.dialog import MDDialog
from components.dialog_flat_button.dialog_flat_button import DialogFlatButton
from components.dialog_edit_word_info.dialog_edit_word_info import DialogEditWordInfo
import utils.db_functions as db
from kivy.clock import Clock


class TranslationDefinitionDiv(MDScreen):
    def __init__(self, **kwargs):
        super(TranslationDefinitionDiv, self).__init__(**kwargs)
        self.word_instance = None

    def on_touch_down(self, touch):
        root = App.get_running_app().root
        reading_screen = root.ids.reading_screen
        if reading_screen.is_card_active and self.collide_point(
                touch.x, touch.y) and touch.y <= self.height * 0.3:
            super().on_touch_down(touch)
            return True
        else:
            pass

    def previous_translation_screen(self):
        root = App.get_running_app().root
        reading_screen = root.ids.reading_screen
        screen_manager = self.ids.translation_card_screen_manager
        if self.ids.previous_screen.opacity == 0:
            return
        if screen_manager.current == 'save_to_dictionary':
            self.ids.translation_scroll_view.scroll_y = 1
            screen_manager.current = 'translation_screen'
            screen_manager.transition.direction = 'right'
            self.ids.next_screen.opacity = 1
        elif screen_manager.current == 'translation_screen':
            self.ids.definition_scroll_view.scroll_y = 1
            screen_manager.current = 'definition_screen'
            screen_manager.transition.direction = 'right'
            self.ids.previous_screen.opacity = 0
        reading_screen.active_text_input.focus = True

    def next_translation_screen(self):
        screen_manager = self.ids.translation_card_screen_manager
        root = App.get_running_app().root
        reading_screen = root.ids.reading_screen
        if self.ids.next_screen.opacity == 0:
            return
        if screen_manager.current == 'definition_screen':
            self.ids.translation_scroll_view.scroll_y = 1
            screen_manager.current = 'translation_screen'
            screen_manager.transition.direction = 'left'
            self.ids.previous_screen.opacity = 1
        elif screen_manager.current == 'translation_screen':
            screen_manager.current = 'save_to_dictionary'
            screen_manager.transition.direction = 'left'
            self.ids.next_screen.opacity = 0
        reading_screen.active_text_input.focus = True

    def create_word_instance(self):
        root = App.get_running_app().root
        reading_screen = root.ids.reading_screen
        word = reading_screen.text_in_english.lower()
        translation = reading_screen.russian_translation
        definition = reading_screen.english_definition
        self.word_instance = Word(word, definition, translation)

    def on_save_to_folder_click(self):
        self.create_word_instance()
        try:
            root = App.get_running_app().root
            db_connection = root.db_connection
            user = root.user
            if db.is_word_already_saved(
                    db_connection, user.id, self.word_instance):
                raise WordAlreadySaved()
            dialog = DialogEditWordInfo(word=self.word_instance)
            dialog.open()
        except WordWithoutTranslationDefinition:
            dialog = DialogOkayButton(
                title='No definition or translation!',
                text='When saving the word or phrase both definition and translation should be present.')
        except WordAlreadySaved:
            dialog = DialogOkayButton(
                title='This word or phrase is already saved!',
                text='If you want to change its translation or definition, please head to the dictionaries section.')
            dialog.open()

    def on_fast_save_click(self):
        self.create_word_instance()
        self.confirmation_dialog = MDDialog(
            title='Are you sure you want to fast save?',
            buttons=[
                DialogFlatButton(
                    text='Yes',
                    on_release=lambda x: self.on_fast_save_confirmation()
                ),
                DialogFlatButton(
                    text='No',
                    on_release=lambda x: self.confirmation_dialog.dismiss()
                )
            ]
        )
        self.confirmation_dialog.open()

    def on_fast_save_confirmation(self):
        self.confirmation_dialog.dismiss()
        try:
            root = App.get_running_app().root
            root.user.fast_save_word(self.word_instance)
            window_height = App.get_running_app().get_window_height()
            window_width = App.get_running_app().get_window_width()
            success_sb = SuccessSnackbar(
                text='The word has been added to dicionary!',
                snackbar_x="10dp",
                snackbar_y=window_height * 0.93,
            )
            success_sb.md_bg_color = 'white'
            success_sb.size_hint_x = (
                window_width - (success_sb.snackbar_x * 2)
            ) / window_width
            success_sb.snackbar_animation_dir = 'Top'
            success_sb.open()
            Clock.schedule_once(lambda dt: success_sb.dismiss(), 1.5)
        except WordWithoutTranslationDefinition:
            dialog = DialogOkayButton(
                title='No definition or translation!',
                text='When saving the word or phrase both definition and translation should be present.')
        except WordAlreadySaved:
            dialog = DialogOkayButton(
                title='This word or phrase is already saved!',
                text='If you want to change its translation or definition, please head to the dictionaries section.')
            dialog.open()

    def on_slide_card_down_click(self):
        root = App.get_running_app().root
        reading_screen = root.ids.reading_screen
        reading_screen.slide_translation_card_down()
