from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivy.clock import Clock
from classes.user import User
import utils.auxillary_functions as aux
import utils.db_functions as db
from components.success_snackbar.success_snackbar import SuccessSnackbar


class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_under_login_click(self):
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
                text='Successfully logged in!',
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
            root.ids.main_screen_manager.current = 'main_screen'

    def validate_login(self, email, password):
        if not aux.are_all_fields_filled(email, password):
            return 'All fields should be filled'
        if not aux.is_valid_email(email):
            return "Invalid email"
        user_id = db.get_user_id_by_email(self.db_connection, email)
        if user_id == -1:
            return "Incorrect email"
        if not aux.is_correct_password(
                password, db.get_password_by_user_id(self.db_connection, user_id)):
            return "Incorrect password"
        return 'OK'

    def login(self):
        root = App.get_running_app().root
        self.db_connection = root.db_connection
        email = self.ids.email_input_login.text
        password = self.ids.password_input_login.text
        res = self.validate_login(email, password)
        if res == 'OK':
            self.ids.email_input_login.text = ''
            self.ids.password_input_login.text = ''
            user_id = db.get_user_id_by_email(self.db_connection, email)
            user_info = self.get_user_info(user_id)
            root.user = User(
                id=user_id,
                **user_info,
                db_connection=self.db_connection)
        self.show_validation_result(res)

    def get_user_info(self, user_id):
        user_info = db.get_all_info_by_user_id(self.db_connection, user_id)
        return user_info
