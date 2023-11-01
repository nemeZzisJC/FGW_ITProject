from kivymd.uix.list import OneLineIconListItem
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
