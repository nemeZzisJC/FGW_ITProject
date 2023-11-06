from kivymd.uix.list import OneLineAvatarIconListItem, OneLineRightIconListItem
from kivy.properties import StringProperty


class WorkoutFolder(OneLineAvatarIconListItem):
    name = StringProperty()

    def __init__(self, id, parent_id, user_id, depth, name, **kwargs):
        self.id = id
        self.parent_id = parent_id
        self.user_id = user_id
        self.depth = depth
        self.name = name
        super().__init__(**kwargs)


class SearchWorkoutFolder(OneLineAvatarIconListItem):
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


class WorkoutFolderWorkout(OneLineRightIconListItem):
    def __init__(self, id, name, workout_type,
                 flashcard_ids=(), cnt=0, **kwargs):
        self.id = id
        self.name = name
        self.workout_type = workout_type
        self.flashcard_ids = flashcard_ids
        self.cnt = cnt
        super().__init__(**kwargs)


class SearchWorkoutFolderWorkout(OneLineRightIconListItem):
    def __init__(self, folder_id, id, name, workout_type,
                 flashcard_ids=(), cnt=0, **kwargs):
        self.folder_id = folder_id
        self.id = id
        self.name = name
        self.workout_type = workout_type
        self.flashcard_ids = flashcard_ids
        self.cnt = cnt
        super().__init__(**kwargs)

    def show_info(self):
        pass
