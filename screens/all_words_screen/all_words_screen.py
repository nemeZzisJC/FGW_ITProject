from kivymd.uix.screen import MDScreen
from kivy.app import App
import utils.db_functions as db
from kivymd.uix.list import IRightBodyTouch, OneLineRightIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from components.dialog_flat_button.dialog_flat_button import DialogFlatButton
from kivymd.uix.dialog import MDDialog


class AllWordsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_selection_active = False

    def search_bar_hint_text_color(self):
        search_bar = self.ids.all_words_search_bar
        if search_bar.text != "":
            search_bar.hint_text_color_normal = [1, 1, 1, 0]
        else:
            search_bar.hint_text_color_normal = 'lightgrey'
        search_bar.set_hint_text_color(search_bar.focus)

    def transition_to_all_storages_screen(self):
        root = App.get_running_app().root
        screen_manager = root.ids.storages_screen_manager
        screen_manager.transition.direction = 'right'
        screen_manager.current = 'all_storages_screen'

    def add_words_to_screen(self):
        self.root_el = App.get_running_app().root
        self.db_connection = self.root_el.db_connection
        user_id = self.root_el.user.id
        words = db.get_all_words_by_user_id(self.db_connection, user_id)
        words_list = self.ids.words_list
        words_list.clear_widgets()
        for word in words:
            words_list.add_widget(CustomWord(word=word['word'], id=word['id'], definition=word['definition'], translation=word['translation'], date=word['date'], text=word['word']))

    def add_some_words_to_screen(self, words):
        words_list = self.ids.words_list
        words_list.clear_widgets()
        for word in words:
            words_list.add_widget(CustomWord(word=word['word'], id=word['id'], definition=word['definition'], translation=word['translation'], date=word['date'], text=word['word']))

    def turn_on_selection_mode(self):
        words_list = self.ids.words_list
        if not self.is_selection_active:
            self.is_selection_active = True
            self.ids.delete_words_button.opacity = 1
            self.ids.delete_words_button.disabled = False
            for child in words_list.children:
                child.ids.right_checkbox.opacity = 1
                child.ids.right_checkbox.disabled = False
        else:
            self.is_selection_active = False
            self.ids.delete_words_button.opacity = 0
            self.ids.delete_words_button.disabled = True
            for child in words_list.children:
                child.ids.right_checkbox.opacity = 0
                child.ids.right_checkbox.disabled = True

    def on_delete_words_confirmation(self):
        self.confirmation_dialog.dismiss()
        word_ids = []
        words_list = self.ids.words_list
        for word in words_list.children:
            if word.ids.right_checkbox.active:
                word_ids.append(word.id)
        db.delete_words_by_ids(self.db_connection, word_ids)
        self.add_words_to_screen()

    def search_bar_response(self, text):
        user_id = self.root_el.user.id
        words = db.get_word_id_by_user_id_and_word_start(self.db_connection, user_id, text)
        self.add_some_words_to_screen(words)

    def on_delete_button_click(self):
        self.confirmation_dialog = MDDialog(
            title='Are you sure you want to delete selected words?',
            text="You won't be able to recover those words after deleting.",
            buttons=[
                DialogFlatButton(
                    text='Yes',
                    on_release=lambda x: self.on_delete_words_confirmation()
                ),
                DialogFlatButton(
                    text='No',
                    on_release=lambda x: self.confirmation_dialog.dismiss()
                )
            ]
        )
        self.confirmation_dialog.open()

class CustomWord(OneLineRightIconListItem):
    def __init__(self, id, definition, translation, word, date, **kwargs):
        self.id = id
        self.definition = definition
        self.translation = translation
        self.word = word
        self.date = date
        super().__init__(**kwargs)

class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass
