import re

# Exceptions that appear when saving the word


class WordSavingError(Exception):
    pass


class WordAlreadySaved(WordSavingError):
    pass


class WordWithoutTranslationDefinition(WordSavingError):
    pass

# Excecptions that appear when updating translation of the word


class TranslationUpdatingError(Exception):
    pass


class EmptyTranslationError(TranslationUpdatingError):
    pass

# Exceptions that appear when updating definition of the word


class DefintionUpdatingError(Exception):
    pass


class EmptyDefintitionError(DefintionUpdatingError):
    pass


class NoDefintionFormatError(DefintionUpdatingError):
    pass


class PartsOfSpeechOnlyError(DefintionUpdatingError):
    pass


class NoLettersError(DefintionUpdatingError):
    pass


class IncorrectStartError(DefintionUpdatingError):
    pass


class IncorrectNumberError(DefintionUpdatingError):
    pass


class PartOfSpeechWithoutDefinitionsError(DefintionUpdatingError):
    pass


class Word:
    _instance = None

    def __new__(cls, word, definition, translation):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        cls._instance.word = word
        cls._instance.definition = definition
        cls._instance.translation = translation
        return cls._instance

    def __init__(self, word, definition, translation):
        self.word = word
        self.definition = definition
        self.translation = translation

    def update_translation(self, new_translation):
        if new_translation != '':
            self.translation = new_translation
        else:
            raise EmptyTranslationError()

    def update_defintion(self, new_definition):
        parts_of_speech = [
            'noun',
            'pronoun',
            'verb',
            'adjective',
            'adverb',
            'preposition',
            'conjunction',
            'interjection',
            'article',
            'determiner',
            'numeral'
        ]
        new_definition = new_definition.strip()
        if not new_definition:
            raise EmptyDefintitionError()
        definition_list = [definition.strip()
                           for definition in new_definition.split('\n')]
        if len(definition_list) == 1:
            if definition_list[0] != 'Definition not found':
                raise NoDefintionFormatError()
            else:
                self.definition = new_definition
        else:
            cnt = 1
            for item in definition_list:
                if item[0].isalpha():
                    if item.lower() not in parts_of_speech:
                        raise PartsOfSpeechOnlyError()
                    else:
                        cnt = 1
                elif item[0].isdigit():
                    number = int(re.match(r'^(\d+)', item).group(1))
                    if all(not symbol.isalpha() for symbol in item):
                        raise NoLettersError()
                    if number != cnt:
                        raise IncorrectNumberError()
                    cnt += 1
                else:
                    raise IncorrectStartError()
            if cnt == 1:
                raise PartOfSpeechWithoutDefinitionsError()
            self.definition = '\n'.join(definition_list)
