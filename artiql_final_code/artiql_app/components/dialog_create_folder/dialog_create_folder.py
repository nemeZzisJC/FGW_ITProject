from kivymd.uix.dialog import MDDialog
from classes.word import *
from components.dialog_flat_button.dialog_flat_button import DialogFlatButton
from components.dialog_okay_button.dialog_okay_button import DialogOkayButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.app import App


class FolderNameError(Exception):
    pass


class InvalidSymbolsError(FolderNameError):
    pass


class FolderNotUnique(FolderNameError):
    pass


class DialogCreateFolderContent(MDBoxLayout):
    def __init__(self, path_to_folder, **kwargs):
        self.path_to_folder = path_to_folder
        super().__init__(**kwargs)


class DialogCreateFolder(MDDialog):
    def __init__(self, path_to_folder, current_folder, **kwargs):
        self.path_to_folder = path_to_folder
        self.current_folder = current_folder
        self.type = 'custom'
        self.content_cls = DialogCreateFolderContent(path_to_folder)
        self.buttons = [
            DialogFlatButton(
                text='Okay',
                on_release=lambda x: self.validate_folder_name()
            ),
            DialogFlatButton(
                text='Cancel',
                on_release=self.dismiss
            )
        ]
        super().__init__(**kwargs)

    def validate_folder_name(self):
        try:
            self.add_folder()
            self.dismiss()
        except InvalidSymbolsError:
            dialog = DialogOkayButton(
                title='Invalid symbols!',
                text='Folder name cannot be empty and has to consist of small Russian or English letters, digits and "_" symbol.'
            )
            dialog.open()
        except FolderNotUnique:
            dialog = DialogOkayButton(
                title="Folder already exists!",
                text='Folder with that name already exists in the current folder.'
            )
            dialog.open()

    def add_folder(self):
        root = App.get_running_app().root
        user = root.user
        folder_name = self.content_cls.ids.folder_name.text
        if aux.folder_name_validation(folder_name):
            if user.is_folder_unique_by_parent_id(
                    self.current_folder, folder_name):
                self.confirmation_dialog = MDDialog(
                    title=f'Add "{folder_name}" folder?',
                    text=f'The folder would be added to the current folder.',
                    buttons=[
                        DialogFlatButton(
                            text='Okay',
                            on_release=lambda x: self.on_adding_folder_confimation(
                                folder_name)
                        ),
                        DialogFlatButton(
                            text='Cancel',
                            on_release=lambda x: self.confirmation_dialog.dismiss()
                        )
                    ]
                )
                self.confirmation_dialog.open()
            else:
                raise FolderNotUnique()
        else:
            raise InvalidSymbolsError()

    def on_adding_folder_confimation(self, folder_name):
        root = App.get_running_app().root
        user = root.user
        user.add_new_folder(self.current_folder, folder_name)
        self.confirmation_dialog.dismiss()
        root.ids.save_to_folder_word_folders_screen.add_folders_to_screen(
            parent_id=self.current_folder)
        root.ids.save_to_folder_word_folders_screen.add_elements_to_screen()
