from random import shuffle
from re import match
import bcrypt
from datetime import datetime, time
import pytz
from tzlocal import get_localzone


def shuffle_article_ids(article_ids):
    shuffle(article_ids)
    return article_ids


def formate_date(d):
    months = [
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'November',
        'October',
        'December']

    year = d[0:4]
    day = str(int(d[8:]))
    month = int(d[5:7]) - 1
    month = months[month]
    return f'{month} {day}, {year}'


def is_valid_email(email):
    accepted_emails = [
        'gmail.com', 'yandex.ru',
        'mail.ru', 'rambler.ru',
        'inbox.ru', 'sendmail.ru',
        'zmail.ru'
    ]
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if match(pattern, email):
        if email[email.index('@') + 1:] in accepted_emails:
            return True
        return False
    else:
        return False


def is_valid_password(password):
    if not (8 <= len(password) <= 35):
        return 'The length of the password should be between 8 and 35'

    if not match("^[a-zA-Z0-9!_]*$", password):
        return 'The password must consist only of a-z, A-Z, 0-9, !, _ symbols'

    if not any(char.isdigit() for char in password):
        return 'The password must contain at least 1 digit'

    if not any(char.isupper() for char in password):
        return 'The password must contain at least 1 capital letter'

    if not any(char.islower() for char in password):
        return 'The password must contain at least 1 non-capital letter'

    return 'OK'


def is_valid_username(username):
    if not (1 <= len(username) <= 45):
        return 'The username length should be between 1 and 45'
    if not match("^[a-zA-Z0-9!_]*$", username):
        return 'The username must consist of a-z, A-Z, 0-9, !, _ symbols'
    return 'OK'


def are_all_fields_filled(*args):
    for arg in args:
        if len(arg) == 0:
            return False
    return True


def hash_password(password):
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)
    return hashed_password


def is_correct_password(input_password, correct_password):
    input_password = input_password.encode('utf-8')
    correct_password = correct_password.encode('utf-8')
    if bcrypt.checkpw(input_password, correct_password):
        return True
    return False


def get_cur_time_str():
    current_date = datetime.now()
    date_string = current_date.strftime('%Y-%m-%d')
    return date_string


def get_cur_time_in_gmt():
    gmt = pytz.timezone('GMT')
    gmt_time = datetime.now(gmt)
    formatted_gmt_time = gmt_time.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_gmt_time


def transform_local_time_to_gmt(local_time_str):
    dt = str_to_datetime(local_time_str)
    local_dt = dt.astimezone()
    local_tz = local_dt.tzinfo
    gmt = pytz.timezone('Etc/GMT')
    local_dt = local_tz.localize(
        datetime.strptime(
            local_time_str,
            '%Y-%m-%d %H:%M:%S'))
    gmt_dt = local_dt.astimezone(gmt)
    return gmt_dt


def datetime_to_str(dt_time):
    return dt_time.strftime(f"%Y-%m-%d %H:%M:%S")


def str_to_datetime(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")


def folder_name_validation(folder_name):
    pattern = r'^[a-zа-я\d_]+$'
    return bool(match(pattern, folder_name))


def transform_gmt_time_to_local_time(gmt_time):
    format = '%Y-%m-%d %H:%M:%S'
    gmt_datetime = datetime.strptime(
        gmt_time, format).replace(
        tzinfo=pytz.timezone('GMT'))
    local_timezone = get_localzone()
    local_datetime = gmt_datetime.astimezone(local_timezone)
    local_time_string = local_datetime.strftime(format)
    return local_time_string


def get_time_difference():
    gmt_time = datetime.utcnow()
    local_time = datetime.now()
    time_difference = local_time - gmt_time
    return time_difference


def get_the_beginning_of_the_day(day):
    return datetime.combine(day, datetime.min.time())


def get_the_end_of_the_day(day):
    return datetime.combine(day, time.max)


def convert_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours} hours, {minutes} minutes, {seconds} seconds"


def round_to_two_decimals(number):
    return round(number, 2)
