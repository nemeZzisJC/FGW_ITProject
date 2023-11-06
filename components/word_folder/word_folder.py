from kivymd.uix.list import OneLineIconListItem, OneLineAvatarIconListItem, OneLineRightIconListItem, IRightBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.properties import StringProperty


class WordFolder(OneLineIconListItem):
    name = StringProperty()

    def __init__(self, id, parent_id, user_id, depth, name, **kwargs):
        self.id = id
        self.parent_id = parent_id
        self.user_id = user_id
        self.depth = depth
        self.name = name
        super().__init__(**kwargs)


class SearchWordFolder(OneLineAvatarIconListItem):
    name = StringProperty()

    def __init__(self, id, parent_id, user_id, depth, name, **kwargs):
        self.id = id
        self.parent_id = parent_id
        self.user_id = user_id
        self.depth = depth
        self.name = name
        super().__init__(**kwargs)

    def show_info(self):
        pass


class SearchWordFolderWord(OneLineRightIconListItem):
    def __init__(self, id, definition, translation, word, date, **kwargs):
        self.id = id
        self.definition = definition
        self.translation = translation
        self.word = word
        self.date = date
        super().__init__(**kwargs)

    def show_info(self):
        pass


class WordFolderWord(OneLineRightIconListItem):
    def __init__(self, id, definition, translation, word, date, **kwargs):
        self.id = id
        self.definition = definition
        self.translation = translation
        self.word = word
        self.date = date
        super().__init__(**kwargs)


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    pass
