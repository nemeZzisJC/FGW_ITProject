from kivymd.uix.screen import MDScreen
from kivy.app import App
import utils.db_functions as db
from components.word_folder.word_folder import WordFolder
from components.dialog_create_folder.dialog_create_folder import DialogCreateFolder
from components.dialog_okay_button.dialog_okay_button import DialogOkayButton
from kivymd.uix.list import OneLineListItem
from kivymd.uix.dialog import MDDialog
from components.dialog_flat_button.dialog_flat_button import DialogFlatButton
from classes.word import WordAlreadySaved

class CustomWordFolder(WordFolder):
    def on_release(self):
        root = App.get_running_app().root
        root.ids.save_to_folder_word_folders_screen.on_folder_click(self)

class SaveToFolderWordFoldersScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.word = None
        self.parent_folder = '-1'
        self.current_folder = '00000000-0000-0000-0000-000000000000'

    def go_back_to_parent_folder(self):
        path_text = self.ids.path_showing_label.text
        ind = path_text.rfind('/')
        if len(path_text[:ind]) == 0:
            self.ids.path_showing_label.text = '/'
        else:
            self.ids.path_showing_label.text = path_text[:ind]
        if self.parent_folder != '-1':
            self.add_folders_to_screen(self.parent_folder)
            self.add_words_to_screen(self.parent_folder)
            print(self.parent_folder)
            try:
                self.parent_folder = db.get_parent_folder_by_id(self.db_connection, self.parent_folder)
            except:
                self.parent_folder = '-1'
        else:
            self.parent_folder = '-1'

    def on_confirmation_add_word_to_current_folder(self):
        user = self.root_el.user
        print(self.word.word)
        print(self.word.translation)
        print(self.word.definition)
        try:
            user.fast_save_word(self.word)
        except Exception as e:
            print(e)
            print('word not unique')
        user.save_word_to_folder(self.current_folder, self.word)
        self.add_words_to_screen(self.current_folder)
        self.confirmation_dialog.dismiss()

    def add_word_to_current_folder(self):
        if db.is_word_unique_in_folder(self.db_connection, self.current_folder, self.word.word):
            self.confirmation_dialog = MDDialog(
                title='Are you sure?',
                text=f'The word "{self.word.word}" would be saved in {self.ids.path_showing_label.text}.',
                buttons=[
                    DialogFlatButton(
                        text='Yes',
                        on_release=lambda x: self.on_confirmation_add_word_to_current_folder()
                    ),
                    DialogFlatButton(
                        text='No',
                        on_release=lambda x: self.confirmation_dialog.dismiss()
                    )
                ]
            )
            self.confirmation_dialog.open()
        else:
            raise WordAlreadySaved()


    def handle_add_word_to_current_folder(self):
        try:
            self.add_word_to_current_folder()
        except:
            folder_name = db.get_folder_name_by_id(self.db_connection, self.current_folder)
            dialog = DialogOkayButton(
                title=f'This word is already saved in "{folder_name}"!',
                text='Please choose another folder',
            )
            dialog.open()

    def create_new_folder(self):
        dialog = DialogCreateFolder(self.ids.path_showing_label.text, self.current_folder)
        dialog.open()

    def on_folder_click(self, folder:WordFolder):
        if self.ids.path_showing_label.text == '/':
            self.ids.path_showing_label.text += folder.name
        else:
            self.ids.path_showing_label.text += '/' + folder.name
        self.parent_folder = folder.parent_id
        self.add_folders_to_screen(folder.id)
        self.add_words_to_screen(folder.id)

    def add_folders_to_screen(self, parent_id):
        self.root_el = App.get_running_app().root
        self.db_connection = self.root_el.db_connection
        user_id = self.root_el.user.id
        child_folders = db.get_child_folders_by_parent_id(self.db_connection, user_id, parent_id)
        folders_list = self.ids.folders_list
        folders_list.clear_widgets()
        for child_folder in child_folders:
            new_item = CustomWordFolder(id=child_folder['id'], parent_id=parent_id, user_id=user_id, depth=child_folder['depth'], name=child_folder['name'])
            folders_list.add_widget(new_item)
        self.current_folder = parent_id

    def add_words_to_screen(self, parent_id):
        user_id = self.root_el.user.id
        words = db.get_only_words_from_folder_by_id(self.db_connection, user_id, self.current_folder)
        print(words)
        folders_list = self.ids.folders_list
        children = folders_list.children[::]
        for child in children:
            if child.__class__.__name__ == 'OneLineListItem':
                folders_list.remove_widget(child)
        for word in words:
            folders_list.add_widget(OneLineListItem(text=word[0]))

    def search_bar_hint_text_color(self):
        search_bar = self.ids.word_folders_search_bar
        if search_bar.text != "":
            search_bar.hint_text_color_normal = [1, 1, 1, 0]
        else:
            search_bar.hint_text_color_normal = 'lightgrey'
        search_bar.set_hint_text_color(search_bar.focus)

    def transition_to_reading_screen(self):
        self.root_el.ids.catalog_screen_manager.transition.direction = 'right'
        self.root_el.ids.catalog_screen_manager.current = 'reading_screen'
        self.ids.path_showing_label.text = '/'
