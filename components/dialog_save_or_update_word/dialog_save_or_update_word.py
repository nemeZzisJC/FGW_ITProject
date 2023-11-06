from kivymd.uix.dialog import MDDialog
from classes.word import Word
from components.dialog_flat_button.dialog_flat_button import DialogFlatButton
from screens.save_to_folder_word_folders_screen.save_to_folder_word_folders_screen import SaveToFolderWordFoldersScreen
from components.dialog_edit_word_info.dialog_edit_word_info import DialogEditWordInfo
from kivymd.uix.boxlayout import MDBoxLayout
from components.dialog_okay_button.dialog_okay_button import DialogOkayButton
from components.word_folder.word_folder import WordFolder, SearchWordFolder
from kivy.app import App


class DialogSaveOrUpdateWordContent(MDBoxLayout):
    def __init__(self, parent_dialog, word_id, word: Word, **kwargs):
        self.word_id = word_id
        self.word = word
        self.parent_dialog = parent_dialog
        super().__init__(**kwargs)

    def on_update_button_click(self):
        dialog = DialogAllWordsUpdateWord(word_id=self.word_id, word=self.word)
        dialog.open()

    def on_save_to_folder_button_click(self):
        self.parent_dialog.dismiss()
        root = App.get_running_app().root
        root.ids.storages_screen_manager.transition.direction = 'left'
        root.ids.storages_screen_manager.current = 'storage_save_to_folder_word_folders_screen'
        save_to_folder_screen = root.ids.storage_save_to_folder_word_folders_screen
        save_to_folder_screen.word = self.word
        save_to_folder_screen.word_id = self.word_id
        save_to_folder_screen.add_folders_to_screen(
            '00000000-0000-0000-0000-000000000000')
        save_to_folder_screen.add_elements_to_screen()


class DialogSaveOrUpdateWord(MDDialog):
    def __init__(self, word_id, word: Word, **kwargs):
        self.word_id = word_id
        self.word = word
        self.type = 'custom'
        self.content_cls = DialogSaveOrUpdateWordContent(
            self, self.word_id, self.word)
        self.buttons = [
            DialogFlatButton(
                text='Cancel',
                on_release=self.dismiss
            )
        ]
        super().__init__(**kwargs)


class DialogAllWordsUpdateWord(DialogEditWordInfo):
    def __init__(self, word_id, word: Word, **kwargs):
        self.word_id = word_id
        super().__init__(word, **kwargs)

    def on_successful_update(self):
        self.confirmation_after_update_dialog = MDDialog(
            title='Are you sure?',
            buttons=[
                DialogFlatButton(
                    text='Yes',
                    on_release=lambda x: self.on_confirmation_after_update()
                ),
                DialogFlatButton(
                    text='No',
                    on_release=lambda x: self.confirmation_after_update_dialog.dismiss()
                )
            ]
        )
        self.confirmation_after_update_dialog.open()

    def on_confirmation_after_update(self):
        self.confirmation_after_update_dialog.dismiss()
        root = App.get_running_app().root
        user = root.user
        user.update_word_definition_translation_by_word_id(
            self.word_id, self.word.definition, self.word.translation)
        self.dismiss()


class SaveFromAllWordsCustomWordFolder(WordFolder):
    def on_release(self):
        root = App.get_running_app().root
        root.ids.storage_save_to_folder_word_folders_screen.on_folder_click(
            self)


class SaveFromAllWordsCustomSearchWordFolder(SearchWordFolder):
    def on_release(self):
        root = App.get_running_app().root
        user = root.user
        save_to_folder_screen = root.ids.storage_save_to_folder_word_folders_screen
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


class SaveFromAllWordsToFolderWordsScreen(SaveToFolderWordFoldersScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.word_id = ''

    def add_folders_to_screen(self, parent_id):
        self.root_el = App.get_running_app().root
        self.db_connection = self.root_el.db_connection
        user = self.root_el.user
        child_folders = user.get_child_word_folders_by_parent_id(parent_id)
        folders_and_elements_list = self.ids.folders_and_elements_list
        folders_and_elements_list.clear_widgets()
        for child_folder in child_folders:
            new_item = SaveFromAllWordsCustomWordFolder(
                id=child_folder['id'],
                parent_id=parent_id,
                user_id=user.id,
                depth=child_folder['depth'],
                name=child_folder['name'])
            folders_and_elements_list.add_widget(new_item)
        self.current_folder = parent_id

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
                    SaveFromAllWordsCustomSearchWordFolder(
                        id=folder['id'],
                        parent_id=folder['parent_id'],
                        user_id=user.id,
                        depth=folder['depth'],
                        name=folder['name']))

    def on_confirmation_add_word_to_current_folder(self):
        user = self.root_el.user
        user.save_word_to_folder(
            self.current_folder,
            self.word,
            word_id=self.word_id)
        self.add_elements_to_screen()
        self.confirmation_dialog.dismiss()
        self.root_el.ids.word_folders_screen.add_folders_to_screen(
            self.current_folder)
        self.root_el.ids.word_folders_screen.add_elements_to_screen()

    def on_back_to_other_screen_click(self):
        self.root_el.ids.storages_screen_manager.transition.direction = 'right'
        self.root_el.ids.storages_screen_manager.current = 'all_words_screen'
        self.ids.path_label.text = '/'
