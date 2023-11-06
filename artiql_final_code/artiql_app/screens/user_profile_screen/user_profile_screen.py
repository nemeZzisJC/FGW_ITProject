from kivymd.uix.screen import MDScreen
from kivymd.uix.pickers import MDDatePicker
from kivy.app import App
from kivy.clock import Clock
from components.dialog_okay_button.dialog_okay_button import DialogOkayButton
import utils.auxillary_functions as aux


class UserProfileScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.show_userename(), 0.1)

    def show_userename(self):
        root = App.get_running_app().root
        if root.user:
            username = root.user.username
            self.ids.hello_user_label.text = 'Hello, ' + username

    def on_show_calendar_click(self):
        date_dialog = MDDatePicker(
            mode='range',
            primary_color='#008080',
            font_name='fonts/Helvetica')
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def show_statistics(self):
        self.ids.workouts_count_layout.opacity = 1
        self.ids.time_training_layout.opacity = 1
        self.ids.correct_answers_layout.opacity = 1

    def hide_statistics(self):
        self.ids.workouts_count_layout.opacity = 0
        self.ids.time_training_layout.opacity = 0
        self.ids.correct_answers_layout.opacity = 0

    def on_save(self, instance, value, date_range):
        if len(date_range) == 0:
            dialog = DialogOkayButton(
                title='You have to choose a date or date range!',
                text='Please choose a date or date range.'
            )
            dialog.open()
        else:
            user = App.get_running_app().root.user
            start_time = aux.get_the_beginning_of_the_day(
                date_range[0]) - aux.get_time_difference()
            end_time = aux.get_the_end_of_the_day(
                date_range[-1]) - aux.get_time_difference()
            info = user.get_user_stats_by_time_range(start_time, end_time)
            # formatting info
            form_workouts_count = aux.round_to_two_decimals(
                info['workouts_count'])
            form_time_training = aux.convert_seconds(
                info['time_training_seconds'])
            correct_answers = info['correct_answers']
            form_workouts_count = aux.round_to_two_decimals(
                info['workouts_count'])
            self.ids.workouts_count_label.text = str(form_workouts_count)
            self.ids.time_training_label.text = form_time_training
            self.ids.correct_answers_label.text = str(correct_answers)
            self.show_statistics()

    def on_cancel(self, instance, value):
        self.hide_statistics()
