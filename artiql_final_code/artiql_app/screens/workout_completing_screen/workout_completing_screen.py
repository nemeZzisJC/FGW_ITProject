from kivymd.uix.screen import MDScreen
from kivy.app import App
import utils.auxillary_functions as aux
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from components.definition_card_part_of_speech_label.definition_card_part_of_speech_label import DefinitionCardPartOfSpeechLabel


class WorkoutCompletingScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.flashcard_ids = []
        self.workout_type = 0
        self.cur_flashcard_ind = 0
        self.correct_answers = 0
        self.partly_correct_answers = 0
        self.wrong_answers = 0
        self.number_of_flashcards = 0
        self.word_has_been_turned = False
        self.workout_start = 0
        self.workout_end = 0

    def show_rating(self):
        self.ids.rate_answer.opacity = 1
        self.ids.correct_answer.opacity = 1
        self.ids.correct_answer.disabled = False
        self.ids.partly_correct_answer.opacity = 1
        self.ids.partly_correct_answer.disabled = False
        self.ids.wrong_answer.opacity = 1
        self.ids.wrong_answer.disabled = False

    def hide_rating(self):
        self.ids.rate_answer.opacity = 0
        self.ids.correct_answer.opacity = 0
        self.ids.correct_answer.disabled = True
        self.ids.partly_correct_answer.opacity = 0
        self.ids.partly_correct_answer.disabled = True
        self.ids.wrong_answer.opacity = 0
        self.ids.wrong_answer.disabled = True

    def change_current_flashcard_ui(self):
        self.root_el = App.get_running_app().root
        user = self.root_el.user
        if self.cur_flashcard_ind >= self.number_of_flashcards:
            self.ids.number_of_flashcards_label.text = str(
                self.number_of_flashcards)
            self.ids.corret_answers_label.text = str(self.correct_answers)
            self.ids.partly_correct_answers_label.text = str(
                self.partly_correct_answers)
            self.ids.wrong_answers_label.text = str(self.wrong_answers)
            self.ids.workout_completing_screen_manager.current = 'results_screen'
        else:
            flashcard_id = self.flashcard_ids[self.cur_flashcard_ind]
            flashcard_info = user.get_all_flashcard_info_by_id(flashcard_id)
            word = flashcard_info['word']
            translation = flashcard_info['translation']
            definition = flashcard_info['definition']
            self.ids.word_or_phrase.text = word
            self.ids.word_information_layout.clear_widgets()
            if flashcard_info['fl_type'] == 2 or flashcard_info['fl_type'] == 3:
                self.ids.word_information_layout.add_widget(
                    DefinitionOnCardComponent(definition=definition))
            if flashcard_info['fl_type'] == 1 or flashcard_info['fl_type'] == 3:
                self.ids.word_information_layout.add_widget(
                    TranslationOnCardComponent(translation=translation))

    def change_flashcard_state(self):
        if self.ids.workout_completing_screen_manager.current == 'word_screen':
            self.ids.workout_completing_screen_manager.current = 'word_information_screen'
        elif self.ids.workout_completing_screen_manager.current == 'word_information_screen':
            self.ids.workout_completing_screen_manager.current = 'word_screen'
        if not self.ids.workout_completing_screen_manager.current == 'results_screen' and self.word_has_been_turned == False:
            self.word_has_been_turned = True
            self.show_rating()

    def on_correct_answer_click(self):
        self.correct_answers += 1
        self.cur_flashcard_ind += 1
        self.ids.workout_completing_screen_manager.current = 'word_screen'
        self.change_current_flashcard_ui()
        self.word_has_been_turned = False
        self.hide_rating()

    def on_partly_correct_answer_click(self):
        self.partly_correct_answers += 1
        self.cur_flashcard_ind += 1
        self.ids.workout_completing_screen_manager.current = 'word_screen'
        self.change_current_flashcard_ui()
        self.word_has_been_turned = False
        self.hide_rating()

    def on_wrong_answer_click(self):
        self.wrong_answers += 1
        self.cur_flashcard_ind += 1
        self.ids.workout_completing_screen_manager.current = 'word_screen'
        self.change_current_flashcard_ui()
        self.word_has_been_turned = False
        self.hide_rating()

    def transition_to_workout_folders_screen(self):
        root = App.get_running_app().root
        user = root.user
        # adding information to user_statistics table
        self.workout_end = aux.get_cur_time_in_gmt()
        user.add_completed_workout_info(
            self.workout_start,
            self.workout_end,
            self.number_of_flashcards,
            self.correct_answers +
            self.partly_correct_answers +
            self.wrong_answers,
            self.correct_answers)
        # updating information for this screen
        self.cur_flashcard_ind = 0
        self.correct_answers = 0
        self.partly_correct_answers = 0
        self.wrong_answers = 0
        self.word_has_been_turned = False
        screen_manager = root.ids.storages_screen_manager
        screen_manager.transition.direction = 'right'
        screen_manager.current = 'workout_folders_screen'
        root.ids.workout_folders_screen.add_folders_to_screen(
            '00000000-0000-0000-0000-000000000000')
        root.ids.workout_folders_screen.add_elements_to_screen()
        root.ids.workout_folders_screen.ids.path_label.text = '/'
        self.ids.workout_completing_screen_manager.current = 'word_screen'
        self.hide_rating()


class DefinitionOnCardComponent(MDBoxLayout):
    def __init__(self, definition, **kwargs):
        self.definition = definition
        super().__init__(**kwargs)
        self.add_definition_to_screen()

    def add_definition_to_screen(self):
        splited_definition = self.definition.split('\n')
        scroll_view_layout = self.ids.definition_scroll_view_layout
        for part in splited_definition:
            if not part:
                continue
            if not part[0].isdigit():
                scroll_view_layout.add_widget(
                    DefinitionCardPartOfSpeechLabel(
                        part_of_speech=part))
            else:
                scroll_view_layout.add_widget(MDLabel(text=part, adaptive_height=True, theme_text_color="Custom", text_color="black", padding=[0, 0, 0, 7],
                                                      font_name='fonts/Helvetica'))


class TranslationOnCardComponent(MDBoxLayout):
    def __init__(self, translation, **kwargs):
        self.translation = translation
        super().__init__(**kwargs)
        self.add_translation_to_screen()

    def add_translation_to_screen(self):
        scroll_view_layout = self.ids.translation_scroll_view_layout
        scroll_view_layout.add_widget(MDLabel(text=self.translation, adaptive_height=True, theme_text_color="Custom", text_color="black", padding=[0, 0, 0, 7],
                                              font_name='fonts/Helvetica'))
