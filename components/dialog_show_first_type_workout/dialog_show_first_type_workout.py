from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from components.dialog_flat_button.dialog_flat_button import DialogFlatButton
from kivy.app import App
from random import shuffle
import utils.auxillary_functions as aux


class DialogShowFirstTypeWorkout(MDDialog):
    def __init__(self, workout_name, workout_cnt, **kwargs):
        self.workout_name = workout_name
        self.workout_cnt = workout_cnt
        self.type = 'custom'
        self.content_cls = DialogShowFirstTypeWorkoutContent(
            self, workout_name=workout_name, workout_cnt=workout_cnt)
        self.buttons = [
            DialogFlatButton(
                text='Cancel',
                on_release=self.dismiss
            )
        ]
        super().__init__(**kwargs)


class DialogShowFirstTypeWorkoutContent(MDBoxLayout):
    def __init__(self, parent_dialog, workout_name,
                 workout_cnt, *args, **kwargs):
        self.parent_dialog = parent_dialog
        self.workout_name = workout_name
        self.workout_cnt = workout_cnt
        super().__init__(*args, **kwargs)

    def on_start_workout_button_click(self):
        # get flashcard_ids
        root = App.get_running_app().root
        flashcard_ids = root.user.get_all_unique_by_word_flashcards_by_user_id()
        flashcard_ids = flashcard_ids[:min(
            len(flashcard_ids), self.workout_cnt)]
        shuffle(flashcard_ids)
        # transition
        self.parent_dialog.dismiss()
        screen_manager = root.ids.storages_screen_manager
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'workout_completing_screen'
        root.ids.workout_completing_screen.workout_type = 1
        root.ids.workout_completing_screen.flashcard_ids = flashcard_ids
        root.ids.workout_completing_screen.number_of_flashcards = min(
            len(flashcard_ids), self.workout_cnt)
        root.ids.workout_completing_screen.workout_start = aux.get_cur_time_in_gmt()
        root.ids.workout_completing_screen.change_current_flashcard_ui()
