import utils.db_functions as db
import utils.auxillary_functions as aux
from classes.word import Word
from classes.word import WordSavingError
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

    def fast_save_word(self, word:Word):
        if word.translation == '-1' or word.definition == '-1':
            raise WordWithoutTranslationDefinition()
        if db.is_word_already_saved(self.db_connection, self.id, word):
            raise WordAlreadySaved()
        print("THE WORD IS UNIQUE")
        date = aux.get_cur_time_in_gmt()
        print(date)
        db.fast_save_word(self.db_connection, self.id, word, date)

    def save_word_to_folder(self, folder_id, word:Word):
        word_id = db.get_word_id_by_user_id_and_word(self.db_connection, self.id, word.word)
        print(word_id)
        db.save_word_to_folder(self.db_connection, self.id, folder_id, word_id)
