from screens.base_folders_and_elements_screen.base_folders_and_elements_screen import BaseFoldersAndElementsScreen
from kivy.app import App
import utils.db_functions as db
from components.flashcard_folder.flashcard_folder import *
from components.dialog_create_folder.dialog_create_folder import *
from components.dialog_okay_button.dialog_okay_button import DialogOkayButton
from kivymd.uix.dialog import MDDialog
from components.dialog_flat_button.dialog_flat_button import DialogFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from components.dialog_show_flashcard_info.dialog_show_flashcard_info import *

# FlaschcardFolder with checkbox


class CustomFlashcardFolder(FlashcardFolder):
    def on_release(self):
        root = App.get_running_app().root
        root.ids.flashcard_folders_screen.on_folder_click(self)

# Flashcard with checkbox


class CustomFlashcardFolderFlashcard(FlashcardFolderFlashcard):
    def on_release(self):
        dialog = DialogShowFlashcardInfoFoldersScreen(
            word_id=self.word_id,
            word=self.word,
            definition=self.definition,
            translation=self.translation,
            folder_id='',
            flashcard_type=self.fl_type)
        dialog.open()

# Добавить SearchFlashcardFolder


class CustomSearchFlashcardFolder(SearchFlashcardFolder):
    def on_release(self):
        root = App.get_running_app().root
        user = root.user
        flashcard_folders_screen = root.ids.flashcard_folders_screen
        flashcard_folders_screen.on_folder_click(self)
        flashcard_folders_screen.ids.elements_search_bar.text = ''
        flashcard_folders_screen.ids.path_label.text = user.get_flashcard_folder_path_by_folder_id(
            self.id, self.depth, self.name)

    def show_info(self):
        root = App.get_running_app().root
        user = root.user
        folder_path = user.get_flashcard_folder_path_by_folder_id(
            self.id, self.depth, self.name)
        folder_path = folder_path[:folder_path.rfind('/')]
        if not folder_path:
            folder_path = '/'
        dialog = DialogOkayButton(
            title='Folder location',
            text=f'Path to folder: {folder_path}'
        )
        dialog.open()

# SearchFlashcard


class CustomSearchFlashcardFolderFlashcard(SearchFlashcardFolderFlashcard):
    def __init__(self, folder_id, id, word_id, fl_type,
                 word, definition, translation, **kwargs):
        super().__init__(
            folder_id,
            id,
            word_id,
            fl_type,
            word,
            definition,
            translation,
            **kwargs)
        root = App.get_running_app().root
        user = root.user
        db_connection = root.db_connection
        self.folder_id = folder_id
        self.depth, self.folder_name = user.get_flashcard_folder_depth_and_name_by_folder_id(
            self.folder_id)
        self.flashcard_path = user.get_flashcard_folder_path_by_folder_id(
            self.folder_id, self.depth, self.folder_name)
        self.folder_parent_id = db.get_flashcard_parent_folder_by_id(
            db_connection, self.folder_id)

    def on_release(self):
        root = App.get_running_app().root
        flashcard_folders_screen = root.ids.flashcard_folders_screen
        flashcard_folders_screen.parent_id = self.folder_parent_id
        flashcard_folders_screen.add_folders_to_screen(self.folder_id)
        flashcard_folders_screen.add_elements_to_screen()
        flashcard_folders_screen.ids.elements_search_bar.text = ''
        flashcard_folders_screen.ids.path_label.text = self.flashcard_path

    def show_info(self):
        dialog = DialogOkayButton(
            title='Flashcard location',
            text=f'Path to flashcard: {self.flashcard_path}'
        )
        dialog.open()

# THE SCREEN ITSELF


class FlashcardFoldersScreen(BaseFoldersAndElementsScreen):
    def __init__(self, **kwargs):
        super().__init__(search_bar_hint_text='Search', **kwargs)
        self.is_selection_active = False
        self.is_workout_selection_active = False
        self.workout_selected_flashcard_ids = []
        self.workout_folder_id_for_selection = ''

    def add_folders_to_screen(self, parent_id):
        self.root_el = App.get_running_app().root
        self.db_connection = self.root_el.db_connection
        user = self.root_el.user
        # icon buttons regulation
        self.is_selection_active = False
        self.ids.selection_mode_button.disabled = False
        self.ids.delete_folders_and_elements_button.opacity = 0
        self.ids.delete_folders_and_elements_button.disabled = True
        self.ids.add_folder_or_element_to_workout_button.opacity = 0
        self.ids.add_folder_or_element_to_workout_button.disabled = True
        if not self.is_workout_selection_active:
            self.ids.add_folder_or_element_button.opacity = 1
            self.ids.add_folder_or_element_button.disabled = False
            self.ids.finish_flashcard_selection_button.opacity = 0
            self.ids.finish_flashcard_selection_button.disabled = True
        else:
            self.ids.add_folder_or_element_button.opacity = 0
            self.ids.add_folder_or_element_button.disabled = True
            self.ids.finish_flashcard_selection_button.opacity = 1
            self.ids.finish_flashcard_selection_button.disabled = False
        # adding folders
        child_folders = user.get_child_flashcard_folders_by_parent_id(
            parent_id)
        folders_and_elements_list = self.ids.folders_and_elements_list
        folders_and_elements_list.clear_widgets()
        for child_folder in child_folders:
            folders_and_elements_list.add_widget(
                CustomFlashcardFolder(
                    id=child_folder['id'],
                    parent_id=parent_id,
                    user_id=user.id,
                    depth=child_folder['depth'],
                    name=child_folder['name']))
        self.current_id = parent_id

    def add_elements_to_screen(self):
        user = self.root_el.user
        flashcard_ids = user.get_flashcard_ids_from_folder_by_folder_id(
            self.current_id)
        # adding elements
        folders_and_elements_list = self.ids.folders_and_elements_list
        children = folders_and_elements_list.children[::]
        for child in children:
            if child.__class__.__name__ in (
                    'CustomFlashcardFolderFlashcard', 'CustomSearchFlashcardFolder'):
                folders_and_elements_list.remove_widget(child)
        for flashcard_id in flashcard_ids:
            flashcard_info = user.get_all_flashcard_info_by_id(flashcard_id)
            folders_and_elements_list.add_widget(
                CustomFlashcardFolderFlashcard(
                    id=flashcard_info['id'],
                    word_id=flashcard_info['word_id'],
                    fl_type=flashcard_info['fl_type'],
                    word=flashcard_info['word'],
                    definition=flashcard_info['definition'],
                    translation=flashcard_info['translation']))

    def on_folder_click(self, folder: CustomFlashcardFolder):
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
                self.parent_id = db.get_flashcard_parent_folder_by_id(
                    self.db_connection, self.parent_id)
            except BaseException:
                self.parent_id = '-1'

    def turn_on_selection_mode(self):
        folders_and_elements_list = self.ids.folders_and_elements_list
        if not self.is_selection_active:
            self.is_selection_active = True
            self.ids.add_folder_or_element_button.opacity = 0
            self.ids.add_folder_or_element_button.disabled = True
            if not self.is_workout_selection_active:
                self.ids.delete_folders_and_elements_button.opacity = 1
                self.ids.delete_folders_and_elements_button.disabled = False
            else:
                self.ids.add_folder_or_element_to_workout_button.opacity = 1
                self.ids.add_folder_or_element_to_workout_button.disabled = False
            for child in folders_and_elements_list.children:
                child.ids.right_checkbox.opacity = 1
                child.ids.right_checkbox.disabled = False
        else:
            self.is_selection_active = False
            if not self.is_workout_selection_active:
                self.ids.add_folder_or_element_button.opacity = 1
                self.ids.add_folder_or_element_button.disabled = False
                self.ids.delete_folders_and_elements_button.opacity = 0
                self.ids.delete_folders_and_elements_button.disabled = True
            else:
                self.ids.add_folder_or_element_button.opacity = 0
                self.ids.add_folder_or_element_button.disabled = True
                self.ids.delete_folders_and_elements_button.opacity = 0
                self.ids.delete_folders_and_elements_button.disabled = True
                self.ids.add_folder_or_element_to_workout_button.opacity = 0
                self.ids.add_folder_or_element_to_workout_button.disabled = True
            for child in folders_and_elements_list.children:
                child.ids.right_checkbox.active = False
                child.ids.right_checkbox.opacity = 0
                child.ids.right_checkbox.disabled = True

    def on_delete_button_click(self):
        self.confirmation_dialog = MDDialog(
            title='Are you sure you want to delete selected flashcards and folders?',
            text="Folders and their content would be deleted without recovery. Flashcards would be deleted from current folder without recovery.",
            buttons=[
                DialogFlatButton(
                    text='Yes',
                    on_release=lambda x: self.on_delete_flashcards_confirmation()
                ),
                DialogFlatButton(
                    text='No',
                    on_release=lambda x: self.confirmation_dialog.dismiss()
                )
            ]
        )
        self.confirmation_dialog.open()

    def on_delete_flashcards_confirmation(self):
        self.confirmation_dialog.dismiss()
        flashcard_ids = [""]
        folder_ids = [""]
        folders_and_elements_list = self.ids.folders_and_elements_list
        for child in folders_and_elements_list.children:
            if child.ids.right_checkbox.active:
                if child.__class__.__name__ == 'CustomFlashcardFolderFlashcard':
                    flashcard_ids.append(child.id)
                elif child.__class__.__name__ == 'CustomFlashcardFolder':
                    folder_ids.append(child.id)
        user = self.root_el.user
        user.delete_flashcard_folders_by_id(folder_ids)
        user.delete_flashcards_from_folder_by_id(
            self.current_id, flashcard_ids)
        self.add_folders_to_screen(self.current_id)
        self.add_elements_to_screen()

    def search_bar_response(self, text):
        user = self.root_el.user
        self.parent_id = '-1'
        self.current_id = '00000000-0000-0000-0000-000000000000'
        self.ids.selection_mode_button.disabled = True
        self.ids.path_label.text = '/'
        self.ids.delete_folders_and_elements_button.opacity = 0
        self.ids.delete_folders_and_elements_button.disabled = True
        self.ids.add_folder_or_element_button.opacity = 0
        self.ids.add_folder_or_element_button.disabled = True
        text = text.strip()
        if not text:
            self.add_folders_to_screen(self.current_id)
            self.add_elements_to_screen()
        else:
            folders_and_elements_list = self.ids.folders_and_elements_list
            folders = user.get_flashcard_folders_by_user_id_and_folder_contain(
                text)
            flashcards_folder_id_and_id = user.get_flashcards_and_folder_ids_from_folders_by_user_id_and_flashcard_contain(
                text)
            folders_and_elements_list.clear_widgets()
            for folder in folders:
                folders_and_elements_list.add_widget(
                    CustomSearchFlashcardFolder(
                        id=folder['id'],
                        parent_id=folder['parent_id'],
                        user_id=user.id,
                        depth=folder['depth'],
                        name=folder['name']))
            for flashcard in flashcards_folder_id_and_id:
                flashcard_info = user.get_all_flashcard_info_by_id(
                    flashcard['id'])
                folders_and_elements_list.add_widget(
                    CustomSearchFlashcardFolderFlashcard(
                        folder_id=flashcard['folder_id'],
                        id=flashcard_info['id'],
                        word_id=flashcard_info['word_id'],
                        fl_type=flashcard_info['fl_type'],
                        word=flashcard_info['word'],
                        definition=flashcard_info['definition'],
                        translation=flashcard_info['translation']))

    def on_back_to_other_screen_click(self):
        if not self.is_workout_selection_active:
            self.root_el.ids.storages_screen_manager.transition.direction = 'right'
            self.root_el.ids.storages_screen_manager.current = 'all_storages_screen'
            self.ids.path_label.text = '/'
        else:
            self.root_el.ids.storages_screen_manager.transition.direction = 'right'
            self.root_el.ids.storages_screen_manager.current = 'workout_folders_screen'
            self.ids.path_label.text = '/'
            self.root_el.ids.workout_folders_screen.ids.path_label.text = '/'
            self.root_el.ids.workout_folders_screen.add_folders_to_screen(
                '00000000-0000-0000-0000-000000000000')
            self.root_el.ids.workout_folders_screen.add_elements_to_screen()
        self.is_workout_selection_active = False
        self.workout_selected_flashcard_ids = []

    def on_add_folder_or_element_to_workout_button_click(self):
        folders_and_elements_list = self.ids.folders_and_elements_list
        flashcard_ids = [""]
        flashcard_folders_ids = [""]
        for child in folders_and_elements_list.children:
            if child.ids.right_checkbox.active:
                if child.__class__.__name__ == 'CustomFlashcardFolder':
                    flashcard_folders_ids.append(child.id)
                elif child.__class__.__name__ == 'CustomFlashcardFolderFlashcard':
                    flashcard_ids.append(child.id)
        if len(flashcard_folders_ids) == 1 and len(flashcard_ids) == 1:
            dialog = DialogOkayButton(
                title='You have to choose something!',
                text='Please choose at least one folder or flashcard.'
            )
            dialog.open()
        else:
            self.confirmation_adding_dialog = MDDialog(
                title='Are you sure you want to add selected folders and flashcards?',
                text="You won't be able to delete what you've chosen when finishing selection.",
                buttons=[
                    DialogFlatButton(
                        text='Yes',
                        on_release=lambda x: self.on_adding_folder_or_element_to_workout_confirmation(
                            flashcard_ids, flashcard_folders_ids)
                    ),
                    DialogFlatButton(
                        text='No',
                        on_release=lambda x: self.confirmation_adding_dialog.dismiss()
                    )]
            )
            self.confirmation_adding_dialog.open()

    def on_adding_folder_or_element_to_workout_confirmation(
            self, flashcard_ids, flashcard_folders_ids):
        user = App.get_running_app().root.user
        self.workout_selected_flashcard_ids += flashcard_ids[::]
        for flashcard_folder_id in flashcard_folders_ids:
            self.workout_selected_flashcard_ids += user. get_all_flashcards_in_folder_by_id(
                flashcard_folder_id)
        self.confirmation_adding_dialog.dismiss()
        self.turn_on_selection_mode()

    def on_finish_flashcard_selection_button_click(self):
        if all([el == "" for el in self.workout_selected_flashcard_ids]):
            dialog = DialogOkayButton(
                title='You have to add something!',
                text='Please add at least one flashcard.'
            )
            dialog.open()
        else:
            flashcard_ids = db.get_all_unique_by_word_flashcards(
                self.db_connection, self.workout_selected_flashcard_ids)
            dialog = DialogShowWorkoutSelectedFlashcards(
                flashcard_ids=flashcard_ids,
                current_folder=self.workout_folder_id_for_selection)
            dialog.open()

    def on_add_folder_or_element_button_click(self):
        path_to_folder = self.ids.path_label.text
        dialog = FlashcardCreateElementOrFolderDialog(
            path_to_folder=path_to_folder, current_folder=self.current_id)
        dialog.open()


# --- DIALOGS ---

# SHOW CREATING VARS DIALOG
class FlashcardCreateElementOrFolderDialogContent(MDBoxLayout):
    def __init__(self, parent_dialog, path_to_folder,
                 current_folder, **kwargs):
        self.parent_dialog = parent_dialog
        self.path_to_folder = path_to_folder
        self.current_folder = current_folder
        super().__init__(**kwargs)

    def on_create_folder_button_click(self):
        dialog = FlashcardFoldersDialogCreateFolder(
            path_to_folder=self.path_to_folder,
            current_folder=self.current_folder)
        dialog.open()
        self.parent_dialog.dismiss()

    def on_create_flashcard_button_click(self):
        root = App.get_running_app().root
        self.parent_dialog.dismiss()
        if root.show_flashcard_instruction_again:
            self.instruction_dialog = MDDialog(
                title='How to choose a word?',
                text='To choose a word turn on selection mode by clicking on a tick button next to search bar on the screen. Then choose a word and click on a tick button that would appear in the bottom of the screen.',
                buttons=[
                    DialogFlatButton(
                        text='Okay',
                        on_release=lambda x: self.instruction_dialog.dismiss()
                    ),
                    DialogFlatButton(
                        text="Don't show this again",
                        on_release=lambda x: self.do_not_show_flashcard_instruction_again()
                    )
                ]
            )
            self.instruction_dialog.open()
        screen_manager = root.ids.storages_screen_manager
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'all_words_screen'
        root.ids.all_words_screen.is_flashcard_selection_active = True
        root.ids.all_words_screen.flashcard_folder_id_for_selection = self.current_folder
        root.ids.all_words_screen.add_words_to_screen()

    def do_not_show_flashcard_instruction_again(self):
        root = App.get_running_app().root
        self.instruction_dialog.dismiss()
        root.show_flashcard_instruction_again = False


class FlashcardCreateElementOrFolderDialog(MDDialog):
    def __init__(self, path_to_folder, current_folder, **kwargs):
        self.path_to_folder = path_to_folder
        self.current_folder = current_folder
        self.type = 'custom'
        self.content_cls = FlashcardCreateElementOrFolderDialogContent(
            self, path_to_folder=self.path_to_folder, current_folder=self.current_folder)
        self.buttons = [
            DialogFlatButton(
                text='Cancel',
                on_release=self.dismiss
            )
        ]
        super().__init__(**kwargs)

# CREATING FOLDER DIALOG


class FlashcardFoldersDialogCreateFolderContent(DialogCreateFolderContent):
    pass


class FlashcardFoldersDialogCreateFolder(DialogCreateFolder):
    def add_folder(self):
        root = App.get_running_app().root
        user = root.user
        folder_name = self.content_cls.ids.folder_name.text
        if aux.folder_name_validation(folder_name):
            if user.is_flashcard_folder_unique_by_parent_id(
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
        user.add_new_flashcard_folder(self.current_folder, folder_name)
        self.confirmation_dialog.dismiss()
        root.ids.flashcard_folders_screen.add_folders_to_screen(
            parent_id=self.current_folder)
        root.ids.flashcard_folders_screen.add_elements_to_screen()

# SHOWING FLASHCARD DIALOG


class DialogShowFlashcardInfoContentFoldersScreen(
        DialogShowFlashcardInfoContent):
    def __init__(self, word_id, word, definition,
                 translation, flashcard_type, **kwargs):
        super().__init__(word_id, word, definition, translation, flashcard_type, **kwargs)

    def check_flashcard_type(self):
        if self.flashcard_type == 1:
            self.ids.type_1.active = True
            self.ids.type_2.disabled = True
            self.ids.type_3.disabled = True
        elif self.flashcard_type == 2:
            self.ids.type_2.active = True
            self.ids.type_1.disabled = True
            self.ids.type_3.disabled = True
        elif self.flashcard_type == 3:
            self.ids.type_3.active = True
            self.ids.type_1.disabled = True
            self.ids.type_2.disabled = True


class DialogShowFlashcardInfoFoldersScreen(MDDialog):
    def __init__(self, word_id, word, definition, translation,
                 folder_id, flashcard_type, **kwargs):
        self.word_id = word_id
        self.word = word
        self.definition = definition
        self.translation = translation
        self.folder_id = folder_id
        self.flashcard_type = flashcard_type
        self.type = 'custom'
        self.content_cls = DialogShowFlashcardInfoContentFoldersScreen(
            self.word_id,
            self.word,
            self.definition,
            self.translation,
            flashcard_type=self.flashcard_type)
        self.buttons = [
            DialogFlatButton(
                text='Okay',
                on_release=lambda x: self.on_okay_button_click()
            )
        ]
        super().__init__(**kwargs)

    def on_okay_button_click(self):
        self.dismiss()

# WORKOUT SHOWING DIALOG


class WorkoutNameFormatError(Exception):
    pass


class WorkoutNameAlreadyExists(Exception):
    pass


class DialogShowWorkoutSelectedFlashcards(MDDialog):
    def __init__(self, flashcard_ids, current_folder, **kwargs):
        self.flashcard_ids = flashcard_ids
        self.current_folder = current_folder
        self.type = 'custom'
        self.content_cls = DialogShowWorkoutSelectedFlashcardsContent(
            flashcard_ids=self.flashcard_ids, current_folder=self.current_folder)
        self.buttons = [
            DialogFlatButton(
                text='Okay',
                on_release=lambda x: self.on_create_workout_selected_click()
            ),
            DialogFlatButton(
                text='Cancel',
                on_release=lambda x: self.dismiss()
            )
        ]
        super().__init__(**kwargs)

    def on_create_workout_selected_click(self):
        try:
            self.validate_workout_selected_creation()
        except WorkoutNameFormatError:
            dialog = DialogOkayButton(
                title='Incorrect workout name!',
                text='Workout name can only consist of small Russain or English letters, digits and "_" symbol.'
            )
            dialog.open()
        except WorkoutNameAlreadyExists:
            dialog = DialogOkayButton(
                title='A workout with this name already exists in the current folder!',
                text='Please, rename a workout.'
            )
            dialog.open()

    def validate_workout_selected_creation(self):
        workout_name = self.content_cls.ids.workout_name.text
        if not aux.folder_name_validation(workout_name):
            raise WorkoutNameFormatError()
        user = App.get_running_app().root.user
        if not user.is_workout_name_unique_in_folder_id(
                self.current_folder, workout_name):
            raise WorkoutNameAlreadyExists()
        self.confiramtion_dialog = MDDialog(
            title=f'Are you sure you want to add "{workout_name}" to current folder?',
            buttons=[
                DialogFlatButton(
                    text='Yes',
                    on_release=lambda x: self.on_add__workout_selected_confirmation(
                        workout_name)
                ),
                DialogFlatButton(
                    text='No',
                    on_release=lambda x: self.confiramtion_dialog.dismiss()
                )
            ]
        )
        self.confiramtion_dialog.open()

    def on_add__workout_selected_confirmation(self, workout_name):
        self.confiramtion_dialog.dismiss()
        root = App.get_running_app().root
        user = root.user
        user.add_workout_with_flashcards_to_folder_by_id(
            self.current_folder, workout_name, self.flashcard_ids)
        self.dismiss()
        root.ids.flashcard_folders_screen.is_workout_selection_active = False
        screen_manager = root.ids.storages_screen_manager
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'workout_folders_screen'
        root.ids.workout_folders_screen.ids.path_label.text = '/'
        root.ids.workout_folders_screen.add_folders_to_screen(
            '00000000-0000-0000-0000-000000000000')
        root.ids.workout_folders_screen.add_elements_to_screen()


class DialogShowWorkoutSelectedFlashcardsContent(MDBoxLayout):
    def __init__(self, flashcard_ids, current_folder, **kwargs):
        self.flashcard_ids = flashcard_ids
        self.current_folder = current_folder
        super().__init__(**kwargs)
        self.add_flashcards_to_screen()

    def add_flashcards_to_screen(self):
        root = App.get_running_app().root
        user = root.user
        flashcards_list = self.ids.flashcards_list
        for flashcard_id in self.flashcard_ids:
            flashcard_info = user.get_all_flashcard_info_by_id(flashcard_id)
            flashcards_list.add_widget(
                CustomFlashcardFolderFlashcard(
                    id=flashcard_info['id'],
                    word_id=flashcard_info['word_id'],
                    fl_type=flashcard_info['fl_type'],
                    word=flashcard_info['word'],
                    definition=flashcard_info['definition'],
                    translation=flashcard_info['translation']))

# SHOWING WORKOUT TYPE 2 DIALOG


class DialogShowSecondTypeWorkout(MDDialog):
    def __init__(self, workout_name, flashcard_ids, **kwargs):
        self.workout_name = workout_name
        self.flashcard_ids = flashcard_ids
        self.type = 'custom'
        self.buttons = [
            DialogFlatButton(
                text='Cancel',
                on_release=self.dismiss
            )
        ]
        self.content_cls = DialogShowSecondTypeWorkoutContent(
            self, workout_name=self.workout_name, flashcard_ids=self.flashcard_ids)
        super().__init__(**kwargs)


class DialogShowSecondTypeWorkoutContent(MDBoxLayout):
    def __init__(self, parent_dialog, workout_name,
                 flashcard_ids, *args, **kwargs):
        self.parent_dialog = parent_dialog
        self.workout_name = workout_name
        self.flashcard_ids = flashcard_ids
        super().__init__(*args, **kwargs)
        self.add_flashcards_to_screen()

    def add_flashcards_to_screen(self):
        root = App.get_running_app().root
        user = root.user
        flashcards_list = self.ids.flashcards_list
        for flashcard_id in self.flashcard_ids:
            flashcard_info = user.get_all_flashcard_info_by_id(flashcard_id)
            flashcards_list.add_widget(
                CustomFlashcardFolderFlashcard(
                    id=flashcard_info['id'],
                    word_id=flashcard_info['word_id'],
                    fl_type=flashcard_info['fl_type'],
                    word=flashcard_info['word'],
                    definition=flashcard_info['definition'],
                    translation=flashcard_info['translation']))

    def on_start_workout_button_click(self):
        # transition
        self.parent_dialog.dismiss()
        root = App.get_running_app().root
        screen_manager = root.ids.storages_screen_manager
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'workout_completing_screen'
        root.ids.workout_completing_screen.workout_type = 1
        root.ids.workout_completing_screen.flashcard_ids = self.flashcard_ids
        root.ids.workout_completing_screen.number_of_flashcards = len(
            self.flashcard_ids)
        root.ids.workout_completing_screen.workout_start = aux.get_cur_time_in_gmt()
        root.ids.workout_completing_screen.change_current_flashcard_ui()
