from kivymd.uix.label import MDLabel


class DefinitionCardNotFoundLabel(MDLabel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'fonts/Helvetica'
