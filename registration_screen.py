from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import BaseSnackbar
from kivy.properties import StringProperty
from kivy.app import App
import utils.db_functions as db
import utils.auxillary_functions as aux
from components.success_snackbar.success_snackbar import SuccessSnackbar
from kivy.clock import Clock


class RegistrationScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_under_register_click(self):
        root = App.get_running_app().root
        root.change_authorization_screen()

    def show_validation_result(self, res):
        if res != 'OK':
            self.ids.error_label.text = res
        else:
            window_height = App.get_running_app().get_window_height()
            window_width = App.get_running_app().get_window_width()
            self.ids.error_label.text = ''
            success_sb = SuccessSnackbar(
                text='Successfully registered!',
                snackbar_x="10dp",
                snackbar_y=window_height - window_height * 0.07,
            )
            success_sb.md_bg_color = 'white'
            success_sb.size_hint_x = (
            window_width - (success_sb.snackbar_x * 2)
            ) / window_width
            success_sb.snackbar_animation_dir = 'Top'
            success_sb.open()
            Clock.schedule_once(lambda dt: success_sb.dismiss(), 1.5)
            root = App.get_running_app().root
            root.change_authorization_screen()

    def validate_registration_data(self, username, email, password):
        if not aux.are_all_fields_filled(username, email, password):
            return 'All fields should be filled'
        if not (aux.is_valid_username(username)) == 'OK':
            return aux.is_valid_username(username)
        if not db.is_username_unique(self.db_connection, username):
            return "This username is already taken"
        if not aux.is_valid_email(email):
            return "Invalid email"
        if not db.is_email_unique(self.db_connection, email):
            return "This email is already registered"
        if not (aux.is_valid_password(password) == 'OK'):
            return aux.is_valid_password(password)
        return 'OK'

    def register(self):
        root = App.get_running_app().root
        self.db_connection = root.db_connection
        username = self.ids.username_input_reg.text
        email = self.ids.email_input_reg.text
        password = self.ids.password_input_reg.text
        res = self.validate_registration_data(username, email, password)
        if res == 'OK':
            db.create_user(self.db_connection, username, email, password)
            db.create_user_registration_date(self.db_connection, username)
        self.show_validation_result(res)
