from kivymd.uix.dialog import MDDialog
from components.dialog_flat_button.dialog_flat_button import DialogFlatButton
from components.dialog_okay_button.dialog_okay_button import DialogOkayButton
from components.definition_card_part_of_speech_label.definition_card_part_of_speech_label import DefinitionCardPartOfSpeechLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.app import App


class FlashcardSavingTypeError(Exception):
    pass


class FlashcardNotUniqueError(Exception):
    pass


class DialogShowFlashcardInfoContent(MDBoxLayout):
    def __init__(self, word_id, word, definition,
                 translation, flashcard_type, **kwargs):
        self.word_id = word_id
        self.word = word
        self.definition = definition
        self.translation = translation
        self.flashcard_type = flashcard_type
        super().__init__(**kwargs)
        self.add_definition_to_screen()
        self.add_translation_to_screen()
        self.check_flashcard_type()

    def check_flashcard_type(self):
        if self.flashcard_type == 1:
            self.ids.type_1.active = True
        elif self.flashcard_type == 2:
            self.ids.type_2.active = True
        elif self.flashcard_type == 3:
            self.ids.type_3.active = True

    def add_translation_to_screen(self):
        scroll_view_layout = self.ids.translation_scroll_view_layout
        scroll_view_layout.add_widget(MDLabel(text=self.translation, adaptive_height=True, theme_text_color="Custom", text_color="black", padding=[0, 0, 0, 7],
                                              font_name='fonts/Helvetica'))

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


class DialogShowFlashcardInfo(MDDialog):
    def __init__(self, word_id, word, definition,
                 translation, folder_id, **kwargs):
        self.word_id = word_id
        self.word = word
        self.definition = definition
        self.translation = translation
        self.folder_id = folder_id
        self.flashcard_type = 0
        self.type = 'custom'
        self.content_cls = DialogShowFlashcardInfoContent(
            self.word_id,
            self.word,
            self.definition,
            self.translation,
            flashcard_type=self.flashcard_type)
        self.buttons = [
            DialogFlatButton(
                text='Okay',
                on_release=lambda x: self.on_okay_button_click()
            ),
            DialogFlatButton(
                text='Cancel',
                on_release=self.dismiss
            )
        ]
        super().__init__(**kwargs)

    def save_flashcard_to_folder(self):
        cnt = 0
        self.saving_type = 0
        if self.content_cls.ids.type_1.active:
            cnt += 1
            self.saving_type = 1
        elif self.content_cls.ids.type_2.active:
            cnt += 1
            self.saving_type = 2
        elif self.content_cls.ids.type_3.active:
            cnt += 1
            self.saving_type = 3
        if cnt != 1:
            raise FlashcardSavingTypeError()
        root = App.get_running_app().root
        user = root.user
        if not user.is_flashcard_unique_in_folder(
                self.word_id, self.folder_id):
            raise FlashcardNotUniqueError()

    def on_okay_button_click(self):
        try:
            self.save_flashcard_to_folder()
            self.flashcard_type = self.saving_type
            self.confirmation_dialog = MDDialog(
                title='Are you sure?',
                text=f'Do you want to save flashcard for  "{self.word}" to the current folder?',
                buttons=[
                    DialogFlatButton(
                        text='Yes',
                        on_release=lambda x: self.on_confirmation_click()
                    ),
                    DialogFlatButton(
                        text='No',
                        on_release=lambda x: self.confirmation_dialog.dismiss()
                    )
                ]
            )
            self.confirmation_dialog.open()
        except FlashcardSavingTypeError:
            dialog = DialogOkayButton(
                title='Choose saving type!',
                text='Saving type should be chosen.'
            )
            dialog.open()
        except FlashcardNotUniqueError:
            dialog = DialogOkayButton(
                title=f'Flashcard for "{self.word}" already exists!',
                text='Flashcard for this word or phrase already exists in current folder.'
            )
            dialog.open()

    def on_confirmation_click(self):
        root = App.get_running_app().root
        user = root.user
        self.confirmation_dialog.dismiss()
        self.dismiss()
        user.add_new_flashcard_to_folder_by_id(
            self.word_id, self.flashcard_type, self.folder_id)
        root.ids.all_words_screen.is_flashcard_selection_active = False
        screen_manager = root.ids.storages_screen_manager
        screen_manager.transition.direction = 'left'
        screen_manager.current = 'flashcard_folders_screen'
        root.ids.flashcard_folders_screen.ids.path_label.text = '/'
        root.ids.flashcard_folders_screen.add_folders_to_screen(
            '00000000-0000-0000-0000-000000000000')
        root.ids.flashcard_folders_screen.add_elements_to_screen()
