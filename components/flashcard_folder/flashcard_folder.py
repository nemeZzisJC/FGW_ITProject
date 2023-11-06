from kivymd.uix.list import OneLineAvatarIconListItem, OneLineRightIconListItem
from kivy.properties import StringProperty


class FlashcardFolder(OneLineAvatarIconListItem):
    name = StringProperty()

    def __init__(self, id, parent_id, user_id, depth, name, **kwargs):
        self.id = id
        self.parent_id = parent_id
        self.user_id = user_id
        self.depth = depth
        self.name = name
        super().__init__(**kwargs)


class SearchFlashcardFolder(OneLineAvatarIconListItem):
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


class FlashcardFolderFlashcard(OneLineRightIconListItem):
    def __init__(self, id, word_id, fl_type, word,
                 definition, translation, **kwargs):
        self.id = id
        self.word_id = word_id
        self.fl_type = fl_type
        self.word = word
        self.definition = definition
        self.translation = translation
        super().__init__(**kwargs)


class SearchFlashcardFolderFlashcard(OneLineRightIconListItem):
    def __init__(self, folder_id, id, word_id, fl_type,
                 word, definition, translation, **kwargs):
        self.folder_id = folder_id
        self.id = id
        self.word_id = word_id
        self.fl_type = fl_type
        self.word = word
        self.definition = definition
        self.translation = translation
        super().__init__(**kwargs)

    def show_info(self):
        pass
