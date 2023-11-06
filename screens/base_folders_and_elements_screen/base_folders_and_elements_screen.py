from kivymd.uix.screen import MDScreen


class BaseFoldersAndElementsScreen(MDScreen):
    def __init__(self, search_bar_hint_text='', back_to_other_screen_opacity=1, back_to_other_screen_disabled=False,
                 selection_mode_button_opacity=1, selection_mode_button_disabled=False, **kwargs):
        super().__init__(**kwargs)
        self.search_bar_hint_text = search_bar_hint_text
        self.back_to_other_screen_opacity = back_to_other_screen_opacity
        self.back_to_other_screen_disabled = back_to_other_screen_disabled
        self.selection_mode_button_opacity = selection_mode_button_opacity
        self.selection_mode_button_disabled = selection_mode_button_disabled
        self.parent_id = '-1'
        self.current_id = '00000000-0000-0000-0000-000000000000'

    def add_folders_to_screen(self, parent_id):
        pass

    def add_elements_to_screen(self):
        pass

    def on_folder_click(self, folder):
        pass

    def go_back_to_parent_folder(self):
        pass

    def go_back_to_other_screen_click(self):
        pass

    def search_bar_response(self, text):
        pass

    def turn_on_selection_mode(self):
        pass

    def search_bar_hint_text_color(self):
        search_bar = self.ids.elements_search_bar
        if search_bar.text != "":
            search_bar.hint_text_color_normal = [1, 1, 1, 0]
        else:
            search_bar.hint_text_color_normal = 'lightgrey'
        search_bar.set_hint_text_color(search_bar.focus)
