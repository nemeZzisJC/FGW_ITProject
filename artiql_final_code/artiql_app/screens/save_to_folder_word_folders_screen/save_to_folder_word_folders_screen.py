from screens.base_folders_and_elements_screen.base_folders_and_elements_screen import BaseFoldersAndElementsScreen
from kivy.app import App
import utils.db_functions as db
from components.word_folder.word_folder import WordFolder, SearchWordFolder
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


class CustomSearchWordFolder(SearchWordFolder):
    def on_release(self):
        root = App.get_running_app().root
        user = root.user
        save_to_folder_screen = root.ids.save_to_folder_word_folders_screen
        save_to_folder_screen.on_folder_click(self)
        save_to_folder_screen.ids.elements_search_bar.text = ''
        save_to_folder_screen.ids.path_label.text = user.get_word_folder_path_by_folder_id(
            self.id, self.depth, self.name)

    def show_info(self):
        root = App.get_running_app().root
        user = root.user
        folder_path = user.get_word_folder_path_by_folder_id(
            self.id, self.depth, self.name)
        folder_path = folder_path[:folder_path.rfind('/')]
        if not folder_path:
            folder_path = '/'
        dialog = DialogOkayButton(
            title='Folder location',
            text=f'Path to folder: {folder_path}'
        )
        dialog.open()


class SaveToFolderWordFoldersScreen(BaseFoldersAndElementsScreen):
    def __init__(self, **kwargs):
        super().__init__(
            search_bar_hint_text='Search folder',
            selection_mode_button_opacity=0,
            selection_mode_button_disabled=True,
            **kwargs)
        self.word = None

    def add_folders_to_screen(self, parent_id):
        self.root_el = App.get_running_app().root
        self.db_connection = self.root_el.db_connection
        user = self.root_el.user
        child_folders = user.get_child_word_folders_by_parent_id(parent_id)
        folders_and_elements_list = self.ids.folders_and_elements_list
        folders_and_elements_list.clear_widgets()
        for child_folder in child_folders:
            new_item = CustomWordFolder(
                id=child_folder['id'],
                parent_id=parent_id,
                user_id=user.id,
                depth=child_folder['depth'],
                name=child_folder['name'])
            folders_and_elements_list.add_widget(new_item)
        self.current_folder = parent_id

    def add_elements_to_screen(self):
        user = self.root_el.user
        words = user.get_only_words_from_word_folder_by_id(self.current_folder)
        folders_and_elements_list = self.ids.folders_and_elements_list
        children = folders_and_elements_list.children[::]
        for child in children:
            if child.__class__.__name__ == 'OneLineListItem':
                folders_and_elements_list.remove_widget(child)
        for word in words:
            folders_and_elements_list.add_widget(OneLineListItem(text=word[0]))

    def on_folder_click(self, folder: WordFolder):
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

    def search_bar_response(self, text):
        user = self.root_el.user
        self.parent_id = '-1'
        self.current_folder = '00000000-0000-0000-0000-000000000000'
        self.ids.path_label.text = '/'
        text = text.strip()
        if not text:
            self.add_folders_to_screen(self.current_folder)
        else:
            folders_and_elements_list = self.ids.folders_and_elements_list
            folders = user.get_folders_by_user_id_and_folder_start(text)
            folders_and_elements_list.clear_widgets()
            for folder in folders:
                folders_and_elements_list.add_widget(
                    CustomSearchWordFolder(
                        id=folder['id'],
                        parent_id=folder['parent_id'],
                        user_id=user.id,
                        depth=folder['depth'],
                        name=folder['name']))

    def create_new_folder(self):
        dialog = DialogCreateFolder(
            self.ids.path_label.text,
            self.current_folder)
        dialog.open()

    def handle_add_word_to_current_folder(self):
        try:
            self.add_word_to_current_folder()
        except BaseException:
            dialog = DialogOkayButton(
                title=f'"{self.word.word}" is already saved in current folder!',
                text='Please choose another folder.',
            )
            dialog.open()

    def add_word_to_current_folder(self):
        user = self.root_el.user
        if user.is_word_unique_in_folder(self.current_folder, self.word.word):
            self.confirmation_dialog = MDDialog(
                title='Are you sure?',
                text=f'The word "{self.word.word}" would be saved in current folder.',
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

    def on_confirmation_add_word_to_current_folder(self):
        user = self.root_el.user
        try:
            user.fast_save_word(self.word)
        except Exception as e:
            pass
        user.save_word_to_folder(self.current_folder, self.word)
        self.add_elements_to_screen()
        self.confirmation_dialog.dismiss()

    def on_back_to_other_screen_click(self):
        self.root_el.ids.catalog_screen_manager.transition.direction = 'right'
        self.root_el.ids.catalog_screen_manager.current = 'reading_screen'
        self.ids.path_label.text = '/'
