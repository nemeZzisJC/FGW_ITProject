import utils.db_functions as db
import utils.auxillary_functions as aux
from classes.word import Word
from classes.word import WordAlreadySaved
from classes.word import WordWithoutTranslationDefinition


class User:
    _instance = None

    def __new__(cls, id, username, email, registration_date, db_connection):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        cls._instance.id = id
        cls._instance.username = username
        cls._instance.email = email
        cls._instance.registration_date = registration_date
        return cls._instance

    def __init__(self, id, username, email, registration_date, db_connection):
        self.id = id
        self.username = username
        self.email = email
        self.registration_date = registration_date
        self.db_connection = db_connection

    def fast_save_word(self, word: Word):
        if word.translation == '-1' or word.definition == '-1':
            raise WordWithoutTranslationDefinition()
        if db.is_word_already_saved(self.db_connection, self.id, word):
            raise WordAlreadySaved()
        date = aux.get_cur_time_in_gmt()
        db.fast_save_word(self.db_connection, self.id, word, date)

    def save_word_to_folder(self, folder_id, word: Word, word_id=None):
        if word_id is None:
            word_id = db.get_word_id_by_user_id_and_word(
                self.db_connection, self.id, word.word)
        db.save_word_to_folder(self.db_connection, self.id, folder_id, word_id)

    def is_word_unique_in_folder(self, folder_id, word: str):
        return db.is_word_unique_in_folder(
            self.db_connection, self.id, folder_id, word)

    def is_folder_unique_by_parent_id(self, parent_id, folder_name):
        return db.is_folder_unique_by_parent_id(
            self.db_connection, self.id, parent_id, folder_name)

    def add_new_folder(self, parent_id, folder_name):
        db.add_new_folder(self.db_connection, parent_id, self.id, folder_name)

    def get_child_word_folders_by_parent_id(self, parent_id):
        return db.get_child_word_folders_by_parent_id(
            self.db_connection, self.id, parent_id)

    def get_only_words_from_word_folder_by_id(self, folder_id):
        return db.get_only_words_from_word_folder_by_id(
            self.db_connection, self.id, folder_id)

    def get_all_words_by_user_id(self):
        return db.get_all_words_by_user_id(self.db_connection, self.id)

    def get_words_by_user_id_and_word_start(self, text):
        return db.get_words_by_user_id_and_word_start(
            self.db_connection, self.id, text)

    def get_words_by_user_id_and_date_and_sign(self, date_start, sign):
        return db.get_words_by_user_id_and_date_and_sign(
            self.db_connection, self.id, date_start, sign)

    def get_folders_by_user_id_and_folder_start(self, folder_start):
        return db.get_folders_by_user_id_and_folder_start(
            self.db_connection, self.id, folder_start)

    def get_word_folder_path_by_folder_id(self, folder_id, depth, folder_name):
        return db.get_word_folder_path_by_folder_id(
            self.db_connection, self.id, folder_id, depth, folder_name)

    def get_words_from_word_folder_by_folder_id(self, folder_id):
        return db.get_words_from_word_folder_by_folder_id(
            self.db_connection, self.id, folder_id)

    def delete_words_by_ids(self, word_ids):
        db.delete_words_by_ids(self.db_connection, self.id, word_ids)

    def delete_word_folders_by_id(self, folder_ids):
        db.delete_word_folders_by_id(self.db_connection, self.id, folder_ids)

    def delete_words_from_words_folder_by_id(self, folder_id, word_ids):
        db.delete_words_from_word_folder_by_id(
            self.db_connection, self.id, folder_id, word_ids)

    def get_words_and_folder_ids_from_folders_by_user_id_and_word_start(
            self, word_start):
        return db.get_words_and_folder_ids_from_folders_by_user_id_and_word_start(
            self.db_connection, self.id, word_start)

    def get_word_folder_depth_and_name_by_folder_id(self, folder_id):
        return db.get_word_folder_depth_and_name_by_folder_id(
            self.db_connection, self.id, folder_id)

    def update_word_definition_translation_by_word_id(
            self, word_id, new_definition, new_translation):
        return db.update_word_definition_translation_by_word_id(
            self.db_connection, self.id, word_id, new_definition, new_translation)

    def get_child_flashcard_folders_by_parent_id(self, parent_id):
        return db.get_child_flashcard_folders_by_parent_id(
            self.db_connection, self.id, parent_id)

    def is_flashcard_folder_unique_by_parent_id(self, parent_id, name):
        return db.is_flashcard_folder_unique_by_parent_id(
            self.db_connection, self.id, parent_id, name)

    def add_new_flashcard_folder(self, parent_id, name):
        db.add_new_flashcard_folder(
            self.db_connection, parent_id, self.id, name)

    def is_flashcard_unique_in_folder(self, word_id, folder_id):
        return db.is_flashcard_unique_in_folder(
            self.db_connection, self.id, word_id, folder_id)

    def add_new_flashcard_to_folder_by_id(self, word_id, type, folder_id):
        db.add_new_flashcard_to_folder_by_id(
            self.db_connection, self.id, word_id, type, folder_id)

    def get_all_flashcard_info_by_id(self, flashcard_id):
        return db.get_all_flashcard_info_by_id(
            self.db_connection, self.id, flashcard_id)

    def get_flashcard_ids_from_folder_by_folder_id(self, folder_id):
        return db.get_flashcard_ids_from_folder_by_folder_id(
            self.db_connection, self.id, folder_id)

    def delete_flashcard_folders_by_id(self, folder_ids):
        db.delete_flashcard_folders_by_id(
            self.db_connection, self.id, folder_ids)

    def delete_flashcards_from_folder_by_id(self, folder_id, flashcard_ids):
        db.delete_flashcards_from_folder_by_id(
            self.db_connection, self.id, folder_id, flashcard_ids)

    def get_flashcard_folders_by_user_id_and_folder_contain(
            self, folder_contain):
        return db.get_flashcard_folders_by_user_id_and_folder_contain(
            self.db_connection, self.id, folder_contain)

    def get_flashcard_folder_path_by_folder_id(self, folder_id, depth, name):
        return db.get_flashcard_folder_path_by_folder_id(
            self.db_connection, self.id, folder_id, depth, name)

    def get_flashcards_and_folder_ids_from_folders_by_user_id_and_flashcard_contain(
            self, flashcard_contain):
        return db.get_flashcards_and_folder_ids_from_folders_by_user_id_and_flashcard_contain(
            self.db_connection, self.id, flashcard_contain)

    def get_flashcard_folder_depth_and_name_by_folder_id(self, folder_id):
        return db. get_flashcard_folder_depth_and_name_by_folder_id(
            self.db_connection, self.id, folder_id)

    def get_child_workout_folders_by_parent_id(self, parent_id):
        return db.get_child_workout_folders_by_parent_id(
            self.db_connection, self.id, parent_id)

    def is_workout_folder_unique_by_parent_id(self, parent_id, name):
        return db.is_workout_folder_unique_by_parent_id(
            self.db_connection, self.id, parent_id, name)

    def add_new_workout_folder(self, parent_id, name):
        return db.add_new_workout_folder(
            self.db_connection, self.id, parent_id, name)

    def is_workout_name_unique_in_folder_id(self, folder_id, name):
        return db.is_workout_name_unique_in_folder_id(
            self.db_connection, self.id, folder_id, name)

    def add_count_workout_to_folder_by_id(self, folder_id, name, cnt):
        db.add_count_workout_to_folder_by_id(
            self.db_connection, self.id, folder_id, name, cnt)

    def get_all_flashcards_in_folder_by_id(self, folder_id):
        return db.get_all_flashcards_in_folder_by_id(
            self.db_connection, self.id, folder_id)

    def add_workout_with_flashcards_to_folder_by_id(
            self, folder_id, name, flashcard_ids):
        db.add_workout_with_flashcards_to_folder_by_id(
            self.db_connection, self.id, folder_id, name, flashcard_ids)

    def get_workout_ids_from_folder_by_folder_id(self, folder_id):
        return db.get_workout_ids_from_folder_by_folder_id(
            self.db_connection, self.id, folder_id)

    def get_all_workout_info_by_id(self, workout_id):
        return db.get_all_workout_info_by_id(
            self.db_connection, self.id, workout_id)

    def delete_workout_folders_by_id(self, folder_ids):
        db.delete_workout_folders_by_id(
            self.db_connection, self.id, folder_ids)

    def delete_workouts_from_folder_by_id(self, folder_id, workout_ids):
        db.delete_workouts_from_folder_by_id(
            self.db_connection, self.id, folder_id, workout_ids)

    def get_workout_folders_by_user_id_and_folder_contain(
            self, folder_contain):
        return db.get_workout_folders_by_user_id_and_folder_contain(
            self.db_connection, self.id, folder_contain)

    def get_workouts_and_folder_ids_from_folders_by_user_id_and_workout_contain(
            self, workout_contain):
        return db.get_workouts_and_folder_ids_from_folders_by_user_id_and_workout_contain(
            self.db_connection, self.id, workout_contain)

    def get_workout_folder_path_by_folder_id(self, folder_id, depth, name):
        return db.get_workout_folder_path_by_folder_id(
            self.db_connection, self.id, folder_id, depth, name)

    def get_workout_folder_depth_and_name_by_folder_id(self, folder_id):
        return db.get_workout_folder_depth_and_name_by_folder_id(
            self.db_connection, self.id, folder_id)

    def get_all_unique_by_word_flashcards_by_user_id(self):
        return db.get_all_unique_by_word_flashcards_by_user_id(
            self.db_connection, self.id)

    def add_completed_workout_info(
            self, workout_start, workout_end, questions_number, answers_number, correct_answers_number):
        return db.add_completed_workout_info(
            self.db_connection, self.id, workout_start, workout_end, questions_number, answers_number, correct_answers_number)

    def get_user_stats_by_time_range(self, start_time, end_time):
        return db.get_user_stats_by_time_range(
            self.db_connection, self.id, start_time, end_time)
