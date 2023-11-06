import requests
import json


def get_definitions(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    response = json.loads(response.text)
    result = {'phonetic': '', 'meanings': []}
    try:
        resp = response[0]
        phonetics = resp['phonetics']
        for phonetic in phonetics:
            if phonetic.get('text'):
                result['phonetic'] = phonetic['text']

        meanings = resp['meanings']
        for meaning in meanings:
            defs = {'part_of_speech': '', 'definitions': []}
            part_of_speech = meaning['partOfSpeech']
            defs['part_of_speech'] = part_of_speech
            definitions = meaning['definitions']
            for definition in definitions:
                defs['definitions'].append(definition['definition'])
            result['meanings'].append(defs)
    except Exception:
        result = -1
    return result
