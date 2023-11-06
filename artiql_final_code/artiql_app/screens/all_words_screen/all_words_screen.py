from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivymd.uix.list import IRightBodyTouch, TwoLineRightIconListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from components.dialog_flat_button.dialog_flat_button import DialogFlatButton
from kivymd.uix.dialog import MDDialog
import utils.auxillary_functions as aux
from components.dialog_save_or_update_word.dialog_save_or_update_word import DialogSaveOrUpdateWord
from classes.word import Word
from components.dialog_show_flashcard_info.dialog_show_flashcard_info import DialogShowFlashcardInfo
from components.dialog_okay_button.dialog_okay_button import DialogOkayButton


class AllWordsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_flashcard_selection_active = False
        self.flashcard_folder_id_for_selection = ''
        self.is_selection_active = False
        self.time_dif = aux.get_time_difference()

    def search_bar_hint_text_color(self):
        search_bar = self.ids.all_words_search_bar
        if search_bar.text != "":
            search_bar.hint_text_color_normal = [1, 1, 1, 0]
        else:
            search_bar.hint_text_color_normal = 'lightgrey'
        search_bar.set_hint_text_color(search_bar.focus)

    def transition_to_all_storages_screen(self):
        root = App.get_running_app().root
        if not self.is_flashcard_selection_active:
            screen_manager = root.ids.storages_screen_manager
            screen_manager.transition.direction = 'right'
            screen_manager.current = 'all_storages_screen'
            self.ids.all_words_search_bar.text = ''
        else:
            screen_manager = root.ids.storages_screen_manager
            screen_manager.transition.direction = 'right'
            screen_manager.current = 'flashcard_folders_screen'
            root.ids.flashcard_folders_screen.ids.path_label.text = '/'
            root.ids.flashcard_folders_screen.add_folders_to_screen(
                '00000000-0000-0000-0000-000000000000')
            root.ids.flashcard_folders_screen.add_elements_to_screen()
        self.is_flashcard_selection_active = False

    def add_words_to_screen(self):
        self.root_el = App.get_running_app().root
        self.db_connection = self.root_el.db_connection
        user = self.root_el.user
        self.ids.select_word_for_flashcard.opacity = 0
        self.ids.select_word_for_flashcard.disabled = True
        self.ids.delete_words_button.opacity = 0
        self.ids.delete_words_button.disabled = True
        words = user.get_all_words_by_user_id()
        words_list = self.ids.words_list
        words_list.clear_widgets()
        for word in words:
            words_list.add_widget(
                CustomWord(
                    word=word['word'],
                    id=word['id'],
                    definition=word['definition'],
                    translation=word['translation'],
                    date=word['date'],
                    text=word['word']))

    def add_some_words_to_screen(self, words):
        words_list = self.ids.words_list
        if not self.is_selection_active:
            self.ids.select_word_for_flashcard.opacity = 0
            self.ids.select_word_for_flashcard.disabled = True
            self.ids.delete_words_button.opacity = 0
            self.ids.delete_words_button.disabled = True
        words_list.clear_widgets()
        for word in words:
            words_list.add_widget(
                CustomWord(
                    word=word['word'],
                    id=word['id'],
                    definition=word['definition'],
                    translation=word['translation'],
                    date=word['date'],
                    text=word['word']))

    def turn_on_selection_mode(self):
        words_list = self.ids.words_list
        if not self.is_selection_active:
            self.is_selection_active = True
            if not self.is_flashcard_selection_active:
                self.ids.delete_words_button.opacity = 1
                self.ids.delete_words_button.disabled = False
            else:
                self.ids.select_word_for_flashcard.opacity = 1
                self.ids.select_word_for_flashcard.disabled = False
            for child in words_list.children:
                child.ids.right_checkbox.opacity = 1
                child.ids.right_checkbox.disabled = False
        else:
            self.is_selection_active = False
            if not self.is_flashcard_selection_active:
                self.ids.delete_words_button.opacity = 0
                self.ids.delete_words_button.disabled = True
            else:
                self.ids.select_word_for_flashcard.opacity = 0
                self.ids.select_word_for_flashcard.disabled = True
            for child in words_list.children:
                child.ids.right_checkbox.active = False
                child.ids.right_checkbox.opacity = 0
                child.ids.right_checkbox.disabled = True

    def on_delete_words_confirmation(self):
        self.confirmation_dialog.dismiss()
        word_ids = []
        words_list = self.ids.words_list
        for word in words_list.children:
            if word.ids.right_checkbox.active:
                word_ids.append(word.id)
        user = self.root_el.user
        user.delete_words_by_ids(word_ids)
        self.add_words_to_screen()

    def search_bar_response(self, text):
        user = self.root_el.user
        text = text.strip()
        self.ids.delete_words_button.opacity = 0
        self.ids.delete_words_button.disabled = True
        if text:
            if text[0] in ('>', '<'):
                text_lst = text.split()
                try:
                    if len(text_lst) == 1:
                        date = text[1:]
                    else:
                        date = text_lst[1] + ' ' + text_lst[2]
                    new_date = aux.str_to_datetime(date) - self.time_dif
                    words = user.get_words_by_user_id_and_date_and_sign(
                        new_date, text[0])
                except BaseException:
                    words = []
            else:
                words = user.get_words_by_user_id_and_word_start(text)
        else:
            words = user.get_words_by_user_id_and_word_start(text)
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

    def transition_to_folder_elements_screen(self):
        screen_manager = self.root_el.ids.storages_screen_manager
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'word_folders_screen'
        word_folders_screen = self.root_el.ids.word_folders_screen
        word_folders_screen.is_flashcard_selection_active = self.is_flashcard_selection_active
        word_folders_screen.flashcard_folder_id_for_selection = self.flashcard_folder_id_for_selection
        word_folders_screen.add_folders_to_screen(
            '00000000-0000-0000-0000-000000000000')
        word_folders_screen.add_elements_to_screen()

    def on_select_word_for_flashcard_click(self):
        word_info = self.validate_word_for_flashcard_selection()
        if word_info == -1:
            dialog = DialogOkayButton(
                title='Incorrect selection!',
                text='You should choose exactly one word from the storage.'
            )
            dialog.open()
        else:
            dialog = DialogShowFlashcardInfo(
                word_id=word_info['word_id'],
                word=word_info['word'],
                definition=word_info['definition'],
                translation=word_info['translation'],
                folder_id=self.flashcard_folder_id_for_selection)
            dialog.open()
            self.is_flashcard_selection_active = False

    def validate_word_for_flashcard_selection(self):
        words_list = self.ids.words_list
        cnt = 0
        needed_info = {
            'word_id': '',
            'translation': '',
            'definition': '',
            'word': ''}
        for child in words_list.children:
            if child.ids.right_checkbox.active:
                cnt += 1
                needed_info['word_id'] = child.id
                needed_info['translation'] = child.translation
                needed_info['definition'] = child.definition
                needed_info['word'] = child.word
                if cnt != 1:
                    return -1
        if cnt != 1:
            return -1
        return needed_info


class CustomWord(TwoLineRightIconListItem):
    def __init__(self, id, definition, translation, word, date, **kwargs):
        self.id = id
        self.definition = definition
        self.translation = translation
        self.word = word
        self.date = aux.datetime_to_str(date)
        self.local_date = aux.transform_gmt_time_to_local_time(self.date)
        super().__init__(**kwargs)

    def on_release(self):
        if not self.ids.right_checkbox.disabled:
            pass
        else:
            dialog = DialogSaveOrUpdateWord(
                word_id=self.id,
                word=Word(
                    word=self.word,
                    definition=self.definition,
                    translation=self.translation))
            dialog.open()


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass
