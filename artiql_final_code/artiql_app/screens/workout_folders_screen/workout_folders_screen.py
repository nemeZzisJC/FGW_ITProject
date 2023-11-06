from screens.base_folders_and_elements_screen.base_folders_and_elements_screen import BaseFoldersAndElementsScreen
from kivy.app import App
import utils.db_functions as db
from components.workout_folder.workout_folder import *
from components.dialog_create_folder.dialog_create_folder import *
from components.dialog_okay_button.dialog_okay_button import DialogOkayButton
from kivymd.uix.dialog import MDDialog
from components.dialog_flat_button.dialog_flat_button import DialogFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from components.dialog_show_flashcard_info.dialog_show_flashcard_info import *
import utils.auxillary_functions as aux
from components.dialog_show_first_type_workout.dialog_show_first_type_workout import DialogShowFirstTypeWorkout
from screens.flashcard_folders_screen.flashcard_folders_screen import DialogShowSecondTypeWorkout


class EmptyFieldsError(Exception):
    pass


class IncorrectFlashcardsNumber(Exception):
    pass


class WorkoutNameFormatError(Exception):
    pass


class WorkoutNameAlreadyExists(Exception):
    pass

# WorkoutFolder with checkbox


class CustomWorkoutFolder(WorkoutFolder):
    def on_release(self):
        root = App.get_running_app().root
        root.ids.workout_folders_screen.on_folder_click(self)

# Workout with checkbox


class CustomWorkoutFolderWorkout(WorkoutFolderWorkout):
    def on_release(self):
        if self.workout_type == 1:
            dialog = DialogShowFirstTypeWorkout(
                workout_name=self.name, workout_cnt=self.cnt)
            dialog.open()
        else:
            dialog = DialogShowSecondTypeWorkout(
                workout_name=self.name, flashcard_ids=self.flashcard_ids)
            dialog.open()

# Добавить SearchWokroutFolder


class CustomSearchWorkoutFolder(SearchWorkoutFolder):
    def on_release(self):
        root = App.get_running_app().root
        user = root.user
        workout_folders_screen = root.ids.workout_folders_screen
        workout_folders_screen.on_folder_click(self)
        workout_folders_screen.ids.elements_search_bar.text = ''
        workout_folders_screen.ids.path_label.text = user.get_workout_folder_path_by_folder_id(
            self.id, self.depth, self.name)

    def show_info(self):
        root = App.get_running_app().root
        user = root.user
        folder_path = user.get_workout_folder_path_by_folder_id(
            self.id, self.depth, self.name)
        folder_path = folder_path[:folder_path.rfind('/')]
        if not folder_path:
            folder_path = '/'
        dialog = DialogOkayButton(
            title='Folder location',
            text=f'Path to folder: {folder_path}'
        )
        dialog.open()

# SearchWorkout


class CustomSearchWorkoutFolderWorkout(SearchWorkoutFolderWorkout):
    def __init__(self, folder_id, id, name, workout_type,
                 flashcard_ids=(), cnt=0, **kwargs):
        super().__init__(folder_id, id, name, workout_type, flashcard_ids, cnt, **kwargs)
        root = App.get_running_app().root
        user = root.user
        db_connection = root.db_connection
        self.folder_id = folder_id
        self.depth, self.folder_name = user.get_workout_folder_depth_and_name_by_folder_id(
            self.folder_id)
        self.workout_path = user.get_workout_folder_path_by_folder_id(
            self.folder_id, self.depth, self.folder_name)
        self.folder_parent_id = db.get_workout_parent_folder_by_id(
            db_connection, self.folder_id)

    def on_release(self):
        root = App.get_running_app().root
        workout_folders_screen = root.ids.workout_folders_screen
        workout_folders_screen.parent_id = self.folder_parent_id
        workout_folders_screen.add_folders_to_screen(self.folder_id)
        workout_folders_screen.add_elements_to_screen()
        workout_folders_screen.ids.elements_search_bar.text = ''
        workout_folders_screen.ids.path_label.text = self.workout_path

    def show_info(self):
        dialog = DialogOkayButton(
            title='Workout location',
            text=f'Path to workout: {self.workout_path}'
        )
        dialog.open()

# THE SCREEN ITSELF


class WorkoutFoldersScreen(BaseFoldersAndElementsScreen):
    def __init__(self, **kwargs):
        super().__init__(search_bar_hint_text='Search', **kwargs)
        self.is_selection_active = False

    def add_folders_to_screen(self, parent_id):
        self.root_el = App.get_running_app().root
        self.db_connection = self.root_el.db_connection
        user = self.root_el.user
        # buttons regulation
        self.is_selection_active = False
        self.ids.selection_mode_button.disabled = False
        self.ids.selection_mode_button.opacity = 1
        self.ids.add_folder_or_element_button.opacity = 1
        self.ids.add_folder_or_element_button.disabled = False
        self.ids.delete_folders_and_elements_button.opacity = 0
        self.ids.delete_folders_and_elements_button.disabled = True
        # adding
        child_folders = user.get_child_workout_folders_by_parent_id(parent_id)
        folders_and_elements_list = self.ids.folders_and_elements_list
        folders_and_elements_list.clear_widgets()
        for child_folder in child_folders:
            folders_and_elements_list.add_widget(
                CustomWorkoutFolder(
                    id=child_folder['id'],
                    parent_id=parent_id,
                    user_id=user.id,
                    depth=child_folder['depth'],
                    name=child_folder['name']))
        self.current_id = parent_id

    def add_elements_to_screen(self):
        user = self.root_el.user
        workout_ids = user.get_workout_ids_from_folder_by_folder_id(
            self.current_id)
        # adding elements
        folders_and_elements_list = self.ids.folders_and_elements_list
        children = folders_and_elements_list.children[::]
        for child in children:
            if child.__class__.__name__ in (
                    'CustomSearchWorkoutFolder', 'CustomSearchWorkoutFolderWorkout'):
                folders_and_elements_list.remove_widget(child)
        for workout_id in workout_ids:
            workout_info = user.get_all_workout_info_by_id(workout_id)
            folders_and_elements_list.add_widget(
                CustomWorkoutFolderWorkout(
                    id=workout_id,
                    name=workout_info['name'],
                    workout_type=workout_info['workout_type'],
                    cnt=workout_info['cnt'],
                    flashcard_ids=workout_info['flashcard_ids']))

    def on_folder_click(self, folder: CustomWorkoutFolder):
        self.ids.selection_mode_button.disabled = False
        self.ids.selection_mode_button.opacity = 1
        if self.ids.path_label.text == '/':
            self.ids.path_label.text += folder.name
        else:
            self.ids.path_label.text += '/' + folder.name
        self.parent_id = folder.parent_id
        self.add_folders_to_screen(folder.id)
        self.add_elements_to_screen()

    def on_delete_button_click(self):
        self.confirmation_dialog = MDDialog(
            title='Are you sure you want to delete selected workouts and folders?',
            text="Folders and their content would be deleted without recovery. Workouts would be deleted from current folder without recovery.",
            buttons=[
                DialogFlatButton(
                    text='Yes',
                    on_release=lambda x: self.on_delete_workouts_confirmation()
                ),
                DialogFlatButton(
                    text='No',
                    on_release=lambda x: self.confirmation_dialog.dismiss()
                )
            ]
        )
        self.confirmation_dialog.open()

    def on_delete_workouts_confirmation(self):
        self.confirmation_dialog.dismiss()
        workout_ids = [""]
        folder_ids = [""]
        folders_and_elements_list = self.ids.folders_and_elements_list
        for child in folders_and_elements_list.children:
            if child.ids.right_checkbox.active:
                if child.__class__.__name__ == 'CustomWorkoutFolderWorkout':
                    workout_ids.append(child.id)
                elif child.__class__.__name__ == 'CustomWorkoutFolder':
                    folder_ids.append(child.id)
        user = self.root_el.user
        user.delete_workout_folders_by_id(folder_ids)
        user.delete_workouts_from_folder_by_id(self.current_id, workout_ids)
        self.add_folders_to_screen(self.current_id)
        self.add_elements_to_screen()

    def turn_on_selection_mode(self):
        folders_and_elements_list = self.ids.folders_and_elements_list
        if not self.is_selection_active:
            self.is_selection_active = True
            self.ids.add_folder_or_element_button.opacity = 0
            self.ids.add_folder_or_element_button.disabled = True
            self.ids.delete_folders_and_elements_button.opacity = 1
            self.ids.delete_folders_and_elements_button.disabled = False
            for child in folders_and_elements_list.children:
                child.ids.right_checkbox.opacity = 1
                child.ids.right_checkbox.disabled = False
        else:
            self.is_selection_active = False
            self.ids.add_folder_or_element_button.opacity = 1
            self.ids.add_folder_or_element_button.disabled = False
            self.ids.delete_folders_and_elements_button.opacity = 0
            self.ids.delete_folders_and_elements_button.disabled = True
            for child in folders_and_elements_list.children:
                child.ids.right_checkbox.active = False
                child.ids.right_checkbox.opacity = 0
                child.ids.right_checkbox.disabled = True

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
            folders = user.get_workout_folders_by_user_id_and_folder_contain(
                text)
            workouts_folder_id_and_id = user.get_workouts_and_folder_ids_from_folders_by_user_id_and_workout_contain(
                text)
            folders_and_elements_list.clear_widgets()
            for folder in folders:
                folders_and_elements_list.add_widget(
                    CustomSearchWorkoutFolder(
                        id=folder['id'],
                        parent_id=folder['parent_id'],
                        user_id=user.id,
                        depth=folder['depth'],
                        name=folder['name']))
            for workout in workouts_folder_id_and_id:
                workout_info = user.get_all_workout_info_by_id(workout['id'])
                folders_and_elements_list.add_widget(
                    CustomSearchWorkoutFolderWorkout(
                        folder_id=workout['folder_id'],
                        id=workout['id'],
                        name=workout_info['name'],
                        workout_type=workout_info['workout_type'],
                        flashcard_ids=workout_info['flashcard_ids']))

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
                self.parent_id = db.get_workout_parent_folder_by_id(
                    self.db_connection, self.parent_id)
            except BaseException:
                self.parent_id = '-1'

    def on_add_folder_or_element_button_click(self):
        path_to_folder = self.ids.path_label.text
        dialog = WorkoutCreateElementOrFolderDialog(
            path_to_folder=path_to_folder, current_folder=self.current_id)
        dialog.open()

    def on_back_to_other_screen_click(self):
        self.root_el.ids.storages_screen_manager.transition.direction = 'right'
        self.root_el.ids.storages_screen_manager.current = 'all_storages_screen'
        self.ids.path_label.text = '/'

# --- DIALOGS ---

# SHOW CREATING VARS DIALOG


class WorkoutCreateElementOrFolderDialogContent(MDBoxLayout):
    def __init__(self, parent_dialog, path_to_folder,
                 current_folder, **kwargs):
        self.parent_dialog = parent_dialog
        self.path_to_folder = path_to_folder
        self.current_folder = current_folder
        super().__init__(**kwargs)

    def on_create_folder_button_click(self):
        dialog = WorkoutFoldersDialogCreateFolder(
            path_to_folder=self.path_to_folder,
            current_folder=self.current_folder)
        dialog.open()
        self.parent_dialog.dismiss()

    def on_create_workout_button_click(self):
        dialog = WorkoutChooseCreationType(current_folder=self.current_folder)
        dialog.open()
        self.parent_dialog.dismiss()

    def do_not_show_flashcard_instruction_again(self):
        # root = App.get_running_app().root
        # self.instruction_dialog.dismiss()
        # root.show_flashcard_instruction_again = False
        pass


class WorkoutCreateElementOrFolderDialog(MDDialog):
    def __init__(self, path_to_folder, current_folder, **kwargs):
        self.path_to_folder = path_to_folder
        self.current_folder = current_folder
        self.type = 'custom'
        self.content_cls = WorkoutCreateElementOrFolderDialogContent(
            self, path_to_folder=self.path_to_folder, current_folder=self.current_folder)
        self.buttons = [
            DialogFlatButton(
                text='Cancel',
                on_release=self.dismiss
            )
        ]
        super().__init__(**kwargs)

# CREATING A FOLDER DIALOG


class WorkoutFoldersDialogCreateFolderContent(DialogCreateFolderContent):
    pass


class WorkoutFoldersDialogCreateFolder(DialogCreateFolder):
    def add_folder(self):
        root = App.get_running_app().root
        user = root.user
        folder_name = self.content_cls.ids.folder_name.text
        if aux.folder_name_validation(folder_name):
            if user.is_workout_folder_unique_by_parent_id(
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
        user.add_new_workout_folder(self.current_folder, folder_name)
        self.confirmation_dialog.dismiss()
        root.ids.workout_folders_screen.add_folders_to_screen(
            parent_id=self.current_folder)
        root.ids.workout_folders_screen.add_elements_to_screen()

# CREATING WORKOUT VARS


class WorkoutChooseCreationType(MDDialog):
    def __init__(self, current_folder, **kwargs):
        self.current_folder = current_folder
        self.type = 'custom'
        self.buttons = [
            DialogFlatButton(
                text='Cancel',
                on_release=self.dismiss
            )
        ]
        self.content_cls = WorkoutChooseCreationTypeContent(
            self, current_folder=self.current_folder)
        super().__init__(**kwargs)


class WorkoutChooseCreationTypeContent(MDBoxLayout):
    def __init__(self, parent_dialog, current_folder, **kwargs):
        self.current_folder = current_folder
        self.parent_dialog = parent_dialog
        super().__init__(**kwargs)

    def on_create_all_flashcards_workout_click(self):
        dialog = WorkoutCountCreateDialog(current_folder=self.current_folder)
        dialog.open()
        self.parent_dialog.dismiss()

    def on_create_selected_flashcards_workout_button_click(self):
        self.parent_dialog.dismiss()
        root = App.get_running_app().root
        screen_manager = root.ids.storages_screen_manager
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'flashcard_folders_screen'
        flashcard_folders_screen = root.ids.flashcard_folders_screen
        flashcard_folders_screen.is_workout_selection_active = True
        flashcard_folders_screen.workout_selected_flashcard_ids = []
        flashcard_folders_screen.workout_folder_id_for_selection = self.current_folder
        flashcard_folders_screen.add_folders_to_screen(
            '00000000-0000-0000-0000-000000000000')
        flashcard_folders_screen.add_elements_to_screen()


# CREATING WORKOUT_COUNT
class WorkoutCountCreateDialog(MDDialog):
    def __init__(self, current_folder, **kwargs):
        self.current_folder = current_folder
        self.type = 'custom'
        self.buttons = [
            DialogFlatButton(
                text='Okay',
                on_release=lambda x: self.on_add_workout_count_click()
            ),
            DialogFlatButton(
                text='Cancel',
                on_release=self.dismiss
            )
        ]
        self.content_cls = WorkoutCountCreateDialogContent(
            self, current_folder=self.current_folder)
        super().__init__(**kwargs)

    def on_add_workout_count_click(self):
        try:
            self.validate_adding()
        except EmptyFieldsError:
            dialog = DialogOkayButton(
                title='All fields should be filled!',
                text='Fill all fields and try again.'
            )
            dialog.open()
        except WorkoutNameFormatError:
            dialog = DialogOkayButton(
                title='Incorrect workout name!',
                text='Workout name can only consist of small Russain or English letters, digits and "_" symbol.'
            )
            dialog.open()
        except IncorrectNumberError:
            dialog = DialogOkayButton(
                title='Incorrect number of workouts!',
                text='Type in a number from 1 to 1000.'
            )
            dialog.open()
        except WorkoutNameAlreadyExists:
            dialog = DialogOkayButton(
                title='A workout with this name already exists in the current folder!',
                text='Please, rename a workout.'
            )
            dialog.open()

    def validate_adding(self):
        workout_name = self.content_cls.ids.workout_name.text.strip()
        number_of_flashcards = self.content_cls.ids.number_of_flashcards.text.strip()
        if not workout_name or not number_of_flashcards:
            raise EmptyFieldsError()
        if not aux.folder_name_validation(workout_name):
            raise WorkoutNameFormatError()
        try:
            cnt = int(number_of_flashcards) * \
                (1 <= int(number_of_flashcards) <= 1000)
            if cnt == 0:
                raise IncorrectNumberError()
            user = App.get_running_app().root.user
            if not user.is_workout_name_unique_in_folder_id(
                    self.current_folder, workout_name):
                raise WorkoutNameAlreadyExists()
            # confirmation dialog
            self.confiramtion_dialog = MDDialog(
                title=f'Are you sure you want to add "{workout_name}" to current folder?',
                buttons=[
                    DialogFlatButton(
                        text='Yes',
                        on_release=lambda x: self.on_add_count_workout_confirmation(
                            workout_name, cnt)
                    ),
                    DialogFlatButton(
                        text='No',
                        on_release=lambda x: self.confiramtion_dialog.dismiss()
                    )
                ]
            )
            self.confiramtion_dialog.open()
        except ValueError:
            raise IncorrectNumberError()

    def on_add_count_workout_confirmation(self, workout_name, cnt):
        root = App.get_running_app().root
        user = root.user
        user.add_count_workout_to_folder_by_id(
            self.current_folder, workout_name, cnt)
        self.confiramtion_dialog.dismiss()
        self.dismiss()
        root.ids.workout_folders_screen.add_folders_to_screen(
            self.current_folder)
        root.ids.workout_folders_screen.add_elements_to_screen()


class WorkoutCountCreateDialogContent(MDBoxLayout):
    def __init__(self, parent_dialog, current_folder, **kwargs):
        self.current_folder = current_folder
        self.parent_dialog = parent_dialog
        super().__init__(**kwargs)
