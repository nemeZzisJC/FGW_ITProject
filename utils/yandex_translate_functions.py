import requests
import json

# doesn't recieve any parametrs, 
# returns IAM token and the expiry time of that token if
# the query was successful, if not returns (-1, -1)
def get_IAM_token():
    url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    data = {
        "yandexPassportOauthToken": "y0_AgAAAAAQanPjAATuwQAAAADvgTKVBtom1Y9bT4CWQUAZSa2iMfmQYUM"
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)
    response = response.json()
    if response.get('iamToken') is not None:
        return (response['iamToken'], response['expiresAt'])
    return (-1, -1)


# recieves text to translate and IMA token as parametrs
# returns the russian translation of the word if everything is fine
# returns -1 if something went wrong
def translate_to_russian(input_text, ima_token):
    IAM_TOKEN = ima_token
    folder_id = 'b1g86e8179o6mjdsu53h'
    target_language = 'ru'
    texts = [input_text]

    body = {
        "targetLanguageCode": target_language,
        "texts": texts,
        "folderId": folder_id,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(IAM_TOKEN)
    }

    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
        json = body,
        headers = headers
    )

    response_dict = json.loads(response.text)
    try:
        tranlastion = response_dict['translations'][0]['text']
        return tranlastion
    except:
        return -1
