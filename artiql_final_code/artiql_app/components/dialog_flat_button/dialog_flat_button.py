from kivymd.uix.button import MDFlatButton


class DialogFlatButton(MDFlatButton):
    text = ''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
