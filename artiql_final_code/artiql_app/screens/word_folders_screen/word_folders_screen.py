from screens.base_folders_and_elements_screen.base_folders_and_elements_screen import BaseFoldersAndElementsScreen
from kivy.app import App
import utils.db_functions as db
from components.word_folder.word_folder import SearchWordFolderWord, WordFolderWord
from kivymd.uix.list import OneLineAvatarIconListItem
from screens.all_words_screen.all_words_screen import RightCheckbox
from components.dialog_okay_button.dialog_okay_button import DialogOkayButton
from kivymd.uix.dialog import MDDialog
from components.dialog_flat_button.dialog_flat_button import DialogFlatButton
from components.dialog_show_flashcard_info.dialog_show_flashcard_info import DialogShowFlashcardInfo
from kivy.properties import StringProperty


class WordFoldersCustomWordFolder(OneLineAvatarIconListItem):
    name = StringProperty()

    def __init__(self, id, parent_id, user_id, depth, name, **kwargs):
        self.id = id
        self.parent_id = parent_id
        self.user_id = user_id
        self.depth = depth
        self.name = name
        super().__init__(**kwargs)

    def on_release(self):
        root = App.get_running_app().root
        root.ids.word_folders_screen.on_folder_click(self)


class WordFoldersRightCheckbox(RightCheckbox):
    pass


class CustomWordFolderWord(WordFolderWord):
    def on_release(self):
        # прописать что происходит при нажатии на слово в обычном режиме (пока
        # ничего, но может появится изменение слова)
        pass


class CustomSearchWordFolderWord(SearchWordFolderWord):
    def __init__(self, folder_id, id, definition,
                 translation, word, date, **kwargs):
        root = App.get_running_app().root
        user = root.user
        db_connection = root.db_connection
        self.folder_id = folder_id
        self.depth, self.folder_name = user.get_word_folder_depth_and_name_by_folder_id(
            self.folder_id)
        self.word_path = user.get_word_folder_path_by_folder_id(
            self.folder_id, self.depth, self.folder_name)
        self.folder_parent_id = db.get_parent_folder_by_id(
            db_connection, self.folder_id)
        super().__init__(id, definition, translation, word, date, **kwargs)

    def on_release(self):
        root = App.get_running_app().root
        word_folders_screen = root.ids.word_folders_screen
        word_folders_screen.parent_id = self.folder_parent_id
        word_folders_screen.add_folders_to_screen(self.folder_id)
        word_folders_screen.add_elements_to_screen()
        word_folders_screen.ids.elements_search_bar.text = ''
        word_folders_screen.ids.path_label.text = self.word_path

    def show_info(self):
        dialog = DialogOkayButton(
            title='Word location',
            text=f'Path to word: {self.word_path}'
        )
        dialog.open()


class WordFoldersScreen(BaseFoldersAndElementsScreen):
    def __init__(self, **kwargs):
        super().__init__(search_bar_hint_text='Search word', **kwargs)
        self.flashcard_folder_id_for_selection = ''
        self.is_flashcard_selection_active = False
        self.is_selection_active = False

    def add_folders_to_screen(self, parent_id):
        self.root_el = App.get_running_app().root
        self.db_connection = self.root_el.db_connection
        user = self.root_el.user
        self.is_selection_active = False
        self.ids.selection_mode_button.disabled = False
        self.ids.selection_mode_button.opacity = 1
        child_folders = user.get_child_word_folders_by_parent_id(parent_id)
        folders_and_elements_list = self.ids.folders_and_elements_list
        folders_and_elements_list.clear_widgets()
        for child_folder in child_folders:
            folders_and_elements_list.add_widget(
                WordFoldersCustomWordFolder(
                    id=child_folder['id'],
                    parent_id=parent_id,
                    user_id=user.id,
                    depth=child_folder['depth'],
                    name=child_folder['name']))
        self.current_id = parent_id

    def add_elements_to_screen(self):
        user = self.root_el.user
        words = user.get_words_from_word_folder_by_folder_id(self.current_id)
        if not self.is_selection_active:
            self.ids.delete_folders_and_elements_button.opacity = 0
            self.ids.delete_folders_and_elements_button.disabled = True
            self.ids.select_word_for_flashcard.opcaity = 0
            self.ids.delete_folders_and_elements_button.disabled = True
        folders_and_elements_list = self.ids.folders_and_elements_list
        children = folders_and_elements_list.children[::]
        for child in children:
            if child.__class__.__name__ in (
                    'CustomWordFolderWord', 'CustomSearchWordFolderWord'):
                folders_and_elements_list.remove_widget(child)
        for word in words:
            folders_and_elements_list.add_widget(
                CustomWordFolderWord(
                    word=word['word'],
                    id=word['id'],
                    definition=word['definition'],
                    translation=word['translation'],
                    date=word['date']))

    def on_folder_click(self, folder: WordFoldersCustomWordFolder):
        self.ids.selection_mode_button.disabled = False
        self.ids.selection_mode_button.opacity = 1
        if self.ids.path_label.text == '/':
            self.ids.path_label.text += folder.name
        else:
            self.ids.path_label.text += '/' + folder.name
        self.parent_id = folder.parent_id
        self.add_folders_to_screen(folder.id)
        self.add_elements_to_screen()

    def go_back_to_parent_folder(self):
        path_text = self.ids.path_label.text
        ind = path_text.rfind('/')
        if len(path_text[:ind]) == 0:
            self.ids.path_label.text = '/'
        else:
            self.ids.path_label.text = path_text[:ind]
        if self.parent_id != '-1':
            self.add_folders_to_screen(self.parent_id)
            self.add_elements_to_screen()
            try:
                self.parent_id = db.get_parent_folder_by_id(
                    self.db_connection, self.parent_id)
            except BaseException:
                self.parent_id = '-1'

    def turn_on_selection_mode(self):
        folders_and_elements_list = self.ids.folders_and_elements_list
        if not self.is_selection_active:
            self.is_selection_active = True
            if not self.is_flashcard_selection_active:
                self.ids.delete_folders_and_elements_button.opacity = 1
                self.ids.delete_folders_and_elements_button.disabled = False
            else:
                self.ids.select_word_for_flashcard.opacity = 1
                self.ids.select_word_for_flashcard.disabled = False
            for child in folders_and_elements_list.children:
                child.ids.right_checkbox.opacity = 1
                child.ids.right_checkbox.disabled = False
        else:
            self.is_selection_active = False
            if not self.is_flashcard_selection_active:
                self.ids.delete_folders_and_elements_button.opacity = 0
                self.ids.delete_folders_and_elements_button.disabled = True
            else:
                self.ids.select_word_for_flashcard.opacity = 0
                self.ids.select_word_for_flashcard.disabled = True
            for child in folders_and_elements_list.children:
                child.ids.right_checkbox.active = False
                child.ids.right_checkbox.opacity = 0
                child.ids.right_checkbox.disabled = True

    def on_delete_button_click(self):
        self.confirmation_dialog = MDDialog(
            title='Are you sure you want to delete selected words and folders?',
            text="Folders and their content would be deleted without recovery. Words would be deleted from current folder without recovery.",
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

    def on_delete_words_confirmation(self):
        self.confirmation_dialog.dismiss()
        word_ids = [""]
        folder_ids = [""]
        folders_and_elements_list = self.ids.folders_and_elements_list
        for child in folders_and_elements_list.children:
            if child.ids.right_checkbox.active:
                if child.__class__.__name__ == 'CustomWordFolderWord':
                    word_ids.append(child.id)
                elif child.__class__.__name__ == 'WordFoldersCustomWordFolder':
                    folder_ids.append(child.id)
        user = self.root_el.user
        user.delete_word_folders_by_id(folder_ids)
        user.delete_words_from_words_folder_by_id(self.current_id, word_ids)
        self.add_folders_to_screen(self.current_id)
        self.add_elements_to_screen()

    def search_bar_response(self, text):
        user = self.root_el.user
        self.parent_id = '-1'
        self.current_id = '00000000-0000-0000-0000-000000000000'
        self.ids.path_label.text = '/'
        self.ids.selection_mode_button.disabled = True
        self.ids.selection_mode_button.opacity = 0.5
        self.ids.delete_folders_and_elements_button.opacity = 0
        self.ids.delete_folders_and_elements_button.disabled = True
        text = text.strip()
        if not text:
            self.add_folders_to_screen(self.current_id)
            self.add_elements_to_screen()
        else:
            folders_and_elements_list = self.ids.folders_and_elements_list
            words = user.get_words_and_folder_ids_from_folders_by_user_id_and_word_start(
                text)
            folders_and_elements_list.clear_widgets()
            for word in words:
                folders_and_elements_list.add_widget(
                    CustomSearchWordFolderWord(
                        folder_id=word['folder_id'],
                        id=word['id'],
                        translation=word['translation'],
                        word=word['word'],
                        date=word['date'],
                        definition=word['definition']))

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

    def validate_word_for_flashcard_selection(self):
        folders_and_elements_list = self.ids.folders_and_elements_list
        cnt = 0
        needed_info = {
            'word_id': '',
            'translation': '',
            'definition': '',
            'word': ''}
        for child in folders_and_elements_list.children:
            if child.__class__.__name__ == 'CustomWordFolderWord':
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

    def on_back_to_other_screen_click(self):
        self.root_el.ids.storages_screen_manager.transition.direction = 'right'
        self.root_el.ids.storages_screen_manager.current = 'all_words_screen'
        self.ids.path_label.text = '/'
