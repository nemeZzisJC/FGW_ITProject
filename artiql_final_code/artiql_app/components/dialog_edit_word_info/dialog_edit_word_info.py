from kivymd.uix.dialog import MDDialog
from classes.word import *
from components.dialog_flat_button.dialog_flat_button import DialogFlatButton
from components.dialog_okay_button.dialog_okay_button import DialogOkayButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
from kivy.app import App


class Content(MDBoxLayout):
    definition_text = StringProperty()
    translation_text = StringProperty()
    word_text = StringProperty()

    def __init__(self, word: Word, **kwargs):
        self.word = word
        self.word_text = word.word
        self.definition_text = self.word.definition
        self.translation_text = self.word.translation
        super().__init__(**kwargs)


class DialogEditWordInfo(MDDialog):
    def __init__(self, word: Word, **kwargs):
        self.word = word
        self.type = 'custom'
        self.content_cls = Content(self.word)
        self.buttons = [
            DialogFlatButton(
                text='Okay',
                on_release=lambda x: self.show_updating_result()
            ),
            DialogFlatButton(
                text='Cancel',
                on_release=self.dismiss
            )
        ]
        super(DialogEditWordInfo, self).__init__(**kwargs)

    def on_successful_update(self):
        self.confirmation_after_update_dialog = MDDialog(
            title='Are you sure you want to continue?',
            text="You won't be able to go back to changing definition on that screen if you continue.",
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
        self.dismiss()
        root = App.get_running_app().root
        root.ids.catalog_screen_manager.transition.direction = 'left'
        root.ids.catalog_screen_manager.current = 'save_to_folder_word_folders_screen'
        root.ids.save_to_folder_word_folders_screen.word = self.word
        root.ids.save_to_folder_word_folders_screen.add_folders_to_screen(
            '00000000-0000-0000-0000-000000000000')
        root.ids.save_to_folder_word_folders_screen.add_elements_to_screen()

    def show_updating_result(self):
        try:
            new_translation = self.content_cls.ids.new_translation_input.text
            new_defintion = self.content_cls.ids.new_definition_input.text
            self.word.update_translation(new_translation)
            self.word.update_defintion(new_defintion)
            self.on_successful_update()
        except EmptyTranslationError:
            dialog = DialogOkayButton(
                title="Translation can't be empty!",
                text="If you don't want to write translation write something like 'No translation' to the field."
            )
            dialog.open()
        except EmptyDefintitionError:
            dialog = DialogOkayButton(
                title="Definition can't be empty!",
                text="If you don't want to write any definition, write 'No definition found' in the field."
            )
            dialog.open()
        except NoDefintionFormatError:
            dialog = DialogOkayButton(
                title="It should be 'No definition found'!",
                text="If you don't want to write any definition, write 'No definition found' in the field."
            )
            dialog.open()
        except PartsOfSpeechOnlyError:
            dialog = DialogOkayButton(
                title="Not numbered lines should be parts of speech!",
                text="In not numbered lines you can only write a part of speech of the word the following numbered definitions describe."
            )
            dialog.open()
        except NoLettersError:
            dialog = DialogOkayButton(
                title="Definitions should contain letters!",
                text="There can't be definitions without letters."
            )
            dialog.open()
        except IncorrectNumberError:
            dialog = DialogOkayButton(
                title="Incorrect number before definition!",
                text="Seems like you've lost count. The numbers before definition should be consecutive. After each new part of speech the first definition after it should be numbered with 1."
            )
            dialog.open()
        except PartOfSpeechWithoutDefinitionsError:
            dialog = DialogOkayButton(
                title="Part of speech without definitions!",
                text="Each listed part of speech should have at least one definition."
            )
            dialog.open()
