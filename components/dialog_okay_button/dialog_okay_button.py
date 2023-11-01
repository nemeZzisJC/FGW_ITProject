from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty
from components.dialog_flat_button.dialog_flat_button import DialogFlatButton

class DialogOkayButton(MDDialog):
    text = StringProperty()
    title = StringProperty()

    def __init__(self, **kwargs):
        self.buttons = [
            DialogFlatButton(
                text='Okay',
                on_release=self.dismiss
            ),
        ]
        super().__init__(**kwargs)
