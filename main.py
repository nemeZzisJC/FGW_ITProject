import os
os.environ['KIVY_IMAGE'] = 'pil'
from kivymd.app import MDApp
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.core.window import Window
import utils.db_functions as db
from kivy.lang import Builder


Builder.load_file('components/success_snackbar/success_snackbar.kv')
Builder.load_file('components/element_paragraph/element_paragraph.kv')
Builder.load_file('components/article_catalog_div/article_catalog_div.kv')
Builder.load_file('components/loading_screen/loading_screen.kv')
Builder.load_file('components/h1_heading/h1_heading.kv')
Builder.load_file('components/element_main_heading_comment_image/element_main_heading_comment_image.kv')
Builder.load_file('components/element_main_heading_comment_image_with_comment/element_main_heading_comment_image_with_comment.kv')
Builder.load_file('components/element_image_comment_author/element_image_comment_author.kv')
Builder.load_file('components/element_image_author/element_image_author.kv')
Builder.load_file('components/element_image_no_comment/element_image_no_comment.kv')
Builder.load_file('components/translation_definition_div/translation_definition_div.kv')
Builder.load_file('components/definition_card_part_of_speech_label/definition_card_part_of_speech_label.kv')
Builder.load_file('components/definition_card_definition_label/definition_card_definition_label.kv')
Builder.load_file('components/definition_card_phonetic_label/definition_card_phonetic_label.kv')
Builder.load_file('components/definition_card_not_found_label/definition_card_not_found_label.kv')
Builder.load_file('components/dialog_okay_button/dialog_okay_button.kv')
Builder.load_file('components/dialog_flat_button/dialog_flat_button.kv')
Builder.load_file('components/dialog_edit_word_info/dialog_edit_word_info.kv')
Builder.load_file('components/dialog_edit_word_info_content/dialog_edit_word_info_content.kv')
Builder.load_file('components/word_folder/word_folder.kv')
Builder.load_file('components/dialog_create_folder/dialog_create_folder.kv')


Window.size = (414, 896)
Window.left = 30
Window.top = 30


class MainInterface(MDRelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        screen_manager = self.ids.main_screen_manager
        screen_manager.current = 'authorization_screen'
        self.category = ''

        # Initializing connection to a database
        self.db_connection = db.connect_to_db()

    def change_authorization_screen(self):
        screen_manager = self.ids.authorization_screen_manager
        if screen_manager.current == 'registration_screen':
            screen_manager.current = 'login_screen'
            screen_manager.transition.direction = 'left'
            self.ids.registration_screen.ids.username_input_reg.text = ''
            self.ids.registration_screen.ids.email_input_reg.text = ''
            self.ids.registration_screen.ids.password_input_reg.text = ''
            self.ids.registration_screen.ids.password_input_reg.password = True
        else:
            screen_manager.current = 'registration_screen'
            screen_manager.transition.direction = 'right'
            self.ids.login_screen.ids.email_input_login.text = ''
            self.ids.login_screen.ids.password_input_login.text = ''
            self.ids.login_screen.ids.password_input_login.password = True


class MainApp(MDApp):
    def build(self):
        # Load the .kv files for each screen
        self.theme_cls.material_style = 'M3'
        mi = MainInterface()
        mi.ids.home_screen.add_in_progress_articles()
        return mi
    
    def get_window_height(self):
        return Window.height
    
    def get_window_width(self):
        return Window.width

if __name__ == '__main__':
    MainApp().run()
