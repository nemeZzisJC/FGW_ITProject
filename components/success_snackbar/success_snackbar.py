from kivymd.uix.snackbar import BaseSnackbar
from kivy.properties import StringProperty

class SuccessSnackbar(BaseSnackbar):
    text = StringProperty(None)
