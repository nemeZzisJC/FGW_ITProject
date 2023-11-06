import mysql.connector
from utils.auxillary_functions import hash_password
from utils.auxillary_functions import get_cur_time_str
from classes.word import Word

# Function to establish a database connection


def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="rc1b-u28yoj5456vhpi7b.mdb.yandexcloud.net",
            user="main_user",
            password="sozsyw-Fewrog-2cybpa",
            port=3306,
            ssl_cert="",
            ssl_key="root.crt",
            database="artiqldb",
        )
        return connection
    except Exception as e:
        return None


# Function to execute a SQL query


def execute_query(connection, query, params=None):
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        return cursor
    except Exception as e:
        return None


# Working with artiqldb functions


def search_bar_server(connection, text, category):
    # getting all article ids with this category
    text = text.lower()
    heading_articles = []
    tag_articles = []
    q = "SELECT id FROM artiqldb.tags WHERE name=%s"
    repl = execute_query(connection, q, (category,))
    tag_id = repl.fetchone()[0]

    q = "SELECT article_id FROM artiqldb.articles_tags WHERE tag_id=%s"
    repl = execute_query(connection, q, (tag_id,))
    article_ids = repl.fetchall()
    article_ids = [f'"{article_id_info[0]}"' for article_id_info in article_ids]

    q = f'SELECT heading, id FROM artiqldb.articles WHERE id IN ({", ".join(article_ids)}) ORDER BY date DESC'
    repl = execute_query(connection, q)
    headings = repl.fetchall()
    for heading_info in headings:
        heading = heading_info[0].lower()
        cur_article_id = heading_info[1]
        if text in heading:
            heading_articles.append(cur_article_id)
        else:
            q = "SELECT tag_id FROM artiqldb.articles_tags WHERE article_id=%s"
            repl = execute_query(connection, q, (cur_article_id,))
            tag_ids = repl.fetchall()
            for tag_id_info in tag_ids:
                tag_id = tag_id_info[0]
                q = "SELECT name FROM artiqldb.tags WHERE id=%s"
                repl = execute_query(connection, q, (tag_id,))
                name = repl.fetchone()[0]
                if text in name:
                    tag_articles.append(cur_article_id)
    return heading_articles + tag_articles


def get_articles(connection, cnt):
    q = "SELECT * FROM artiqldb.articles"
    repl = execute_query(connection, q)
    articles = repl.fetchall()[:cnt]
    return articles


def get_articles_by_tag(connection, tag):
    # getting id of the tag
    q = "SELECT id FROM artiqldb.tags WHERE name=%s"
    repl = execute_query(connection, q, (tag,))
    tag_id = repl.fetchone()[0]

    # getting ids of the articles with that tag_id
    q = "SELECT article_id FROM artiqldb.articles_tags WHERE tag_id=%s"
    repl = execute_query(connection, q, (tag_id,))
    article_ids = repl.fetchall()
    article_ids = [article_id[0] for article_id in article_ids]

    return article_ids


def get_article_by_id(connection, article_id):
    q = "SELECT * FROM artiqldb.articles WHERE id=%s"
    repl = execute_query(connection, q, (article_id,))
    article = repl.fetchall()[0]
    return article


def get_article_id_by_heading(connection, heading):
    q = "SELECT id FROM artiqldb.articles WHERE heading=%s"
    repl = execute_query(connection, q, (heading,))
    article_id = repl.fetchone()[0]
    return article_id


def get_main_heading_info_by_article_id(connection, article_id):
    # getting the first element of the article a.k.a. main_heading either with
    # or without comment (summary)
    q = "SELECT * FROM artiqldb.articles_elements WHERE article_id=%s ORDER BY `order`"
    repl = execute_query(connection, q, (article_id,))
    first_article_element = repl.fetchall()[0]
    element_type_id = first_article_element[1]
    element_id = first_article_element[2]

    # getting the name of the element_type by element_type_id
    q = "SELECT name FROM artiqldb.element_type WHERE id=%s"
    repl = execute_query(connection, q, (element_type_id,))
    element_type = repl.fetchone()[0]

    return (element_type, element_type_id, element_id)


def get_main_heading_comment_by_element_id(connection, element_name, element_id):
    table_name = "element_" + element_name
    q = f"SELECT comment FROM artiqldb.{table_name} WHERE id=%s"
    repl = execute_query(connection, q, (element_id,))
    comment = repl.fetchone()[0]
    return comment


def is_username_unique(connection, username):
    q = f"SELECT username FROM artiqldb.users WHERE username=%s"
    repl = execute_query(connection, q, (username,))
    res = repl.fetchall()
    if len(res) == 0:
        return True
    else:
        return False


def is_email_unique(connection, email):
    q = f"SELECT email FROM artiqldb.users WHERE email=%s"
    repl = execute_query(connection, q, (email,))
    res = repl.fetchall()
    if len(res) == 0:
        return True
    else:
        return False


def create_user(connection, username, email, password):
    q = f"INSERT INTO artiqldb.users (id, username, email, password) VALUE (uuid(), %s, %s, %s)"
    hashed_password = hash_password(password)
    execute_query(
        connection,
        q,
        (
            username,
            email,
            hashed_password,
        ),
    )
    connection.commit()


def create_user_registration_date(connection, username):
    q = f"SELECT id FROM artiqldb.users WHERE username=%s"
    repl = execute_query(connection, q, (username,))
    user_id = repl.fetchone()[0]
    q = f"INSERT INTO artiqldb.users_registration_date (user_id, date) VALUE (%s, %s)"
    date = get_cur_time_str()
    execute_query(
        connection,
        q,
        (
            user_id,
            date,
        ),
    )
    connection.commit()


def get_user_id_by_email(connection, email):
    q = "SELECT * FROM artiqldb.users WHERE email=%s"
    repl = execute_query(connection, q, (email,))
    try:
        user_id = repl.fetchone()[0]
        return user_id
    except Exception:
        return -1


def get_password_by_user_id(connection, user_id):
    q = "SELECT password FROM artiqldb.users WHERE id=%s"
    repl = execute_query(connection, q, (user_id,))
    password = repl.fetchone()[0]
    return password


def get_all_info_by_user_id(connection, user_id):
    q = "SELECT * FROM artiqldb.users WHERE id=%s"
    repl = execute_query(connection, q, (user_id,))
    basic_info = repl.fetchone()[1:]
    q = "SELECT date FROM artiqldb.users_registration_date WHERE user_id=%s"
    repl = execute_query(connection, q, (user_id,))
    registration_date = repl.fetchone()[0]
    return {
        "username": basic_info[0],
        "email": basic_info[1],
        "registration_date": registration_date,
    }


def get_article_elements(connection, article_id):
    q = "SELECT element_type_id, element_id, `order` FROM artiqldb.articles_elements WHERE article_id=%s ORDER BY `order` ASC"
    repl = execute_query(connection, q, (article_id,))
    all_elements = repl.fetchall()
    return all_elements


def get_element_info(connection, element_type_id, element_id):
    # getting the name of the element type with that id
    q = "SELECT name FROM artiqldb.element_type WHERE id=%s"
    repl = execute_query(connection, q, (element_type_id,))
    element_class_name = repl.fetchone()[0]
    # getting the element with cur element_id and cur element_class_name
    q = f"SELECT * FROM artiqldb.element_{element_class_name} WHERE id=%s"
    repl = execute_query(connection, q, (element_id,))
    element_info = repl.fetchone()
    # getting the names of the columns
    q = f"SHOW COLUMNS FROM artiqldb.element_{element_class_name}"
    repl = execute_query(connection, q)
    all_columns = repl.fetchall()
    column_names = [column[0] for column in all_columns]
    # creating a dict column_name -> column_value
    dict_element_info = {"element_class_name": element_class_name}
    for i in range(len(column_names)):
        dict_element_info[column_names[i]] = element_info[i]
    return dict_element_info


# Working with words


def is_word_already_saved(connection, user_id, word: Word):
    q = "SELECT id FROM artiqldb.words WHERE user_id=%s AND word=%s"
    repl = execute_query(
        connection,
        q,
        (
            user_id,
            word.word,
        ),
    )
    res = repl.fetchall()
    if len(res) != 0:
        return True
    return False


def get_word_id_by_user_id_and_word(connection, user_id, word):
    q = "SELECT id FROM artiqldb.words WHERE user_id=%s AND word=%s"
    repl = execute_query(
        connection,
        q,
        (
            user_id,
            word,
        ),
    )
    word_id = repl.fetchone()[0]
    return word_id


def get_words_by_user_id_and_word_start(connection, user_id, word_start):
    q = f"""SELECT *
        FROM artiqldb.words
        WHERE word LIKE '{word_start}%' AND user_id = %s
        ORDER BY date DESC"""
    repl = execute_query(connection, q, (user_id,))
    words = repl.fetchall()
    words_dict = []
    for element in words:
        word_info = {
            "id": element[0],
            "word": element[2],
            "definition": element[3],
            "translation": element[4],
            "date": element[5],
        }
        words_dict.append(word_info)
    return words_dict


def get_words_and_folder_ids_from_folders_by_user_id_and_word_start(
    connection, user_id, word_start
):
    q = f"""SELECT fld.folder_id, words.*
        FROM artiqldb.word_folder_words as fld
        INNER JOIN
        artiqldb.words as words ON
        fld.word_id = words.id AND fld.user_id = %s AND words.user_id = fld.user_id
        WHERE words.word LIKE '{word_start}%'
        ORDER BY words.date DESC"""
    repl = execute_query(connection, q, (user_id,))
    words = repl.fetchall()
    words_dict = []
    for element in words:
        word_info = {
            "folder_id": element[0],
            "id": element[1],
            "word": element[3],
            "definition": element[4],
            "translation": element[5],
            "date": element[6],
        }
        words_dict.append(word_info)
    return words_dict


def get_words_by_user_id_and_date_and_sign(connection, user_id, date_start, sign):
    try:
        q = f"""SELECT *
            FROM artiqldb.words
            WHERE date {sign} %s AND user_id = %s
            ORDER BY date DESC"""
        repl = execute_query(
            connection,
            q,
            (
                date_start,
                user_id,
            ),
        )
        words = repl.fetchall()
        words_dict = []
        for element in words:
            word_info = {
                "id": element[0],
                "word": element[2],
                "definition": element[3],
                "translation": element[4],
                "date": element[5],
            }
            words_dict.append(word_info)
        return words_dict
    except BaseException:
        return []


def fast_save_word(connection, user_id, word: Word, date):
    q = "INSERT INTO artiqldb.words (id, user_id, word, definition, translation, date) VALUES (uuid(), %s, %s, %s, %s, %s)"
    execute_query(
        connection,
        q,
        (
            user_id,
            word.word,
            word.definition,
            word.translation,
            date,
        ),
    )
    connection.commit()


def get_child_word_folders_by_parent_id(connection, user_id, parent_id):
    q = "SELECT * FROM artiqldb.word_folders WHERE parent_id=%s AND user_id=%s ORDER BY name ASC"
    repl = execute_query(
        connection,
        q,
        (
            parent_id,
            user_id,
        ),
    )
    folders = repl.fetchall()
    folders_dict = []
    for element in folders:
        new_folder = {
            "id": element[0],
            "parent_id": element[1],
            "user_id": element[2],
            "depth": element[3],
            "name": element[4],
        }
        folders_dict.append(new_folder)
    return folders_dict


def get_only_words_from_word_folder_by_id(connection, user_id, folder_id):
    q = "SELECT words.word FROM artiqldb.word_folder_words as fld INNER JOIN artiqldb.words as words ON fld.word_id =  words.id AND fld.folder_id = %s AND fld.user_id=%s ORDER BY words.date DESC"
    repl = execute_query(
        connection,
        q,
        (
            folder_id,
            user_id,
        ),
    )
    words = repl.fetchall()
    return words


def is_folder_unique_by_parent_id(connection, user_id, parent_id, name):
    q = "SELECT id FROM artiqldb.word_folders WHERE parent_id=%s AND name=%s AND user_id=%s"
    repl = execute_query(connection, q, (parent_id, name, user_id))
    res = repl.fetchall()
    if res:
        return False
    return True


def add_new_folder(connection, parent_id, user_id, name):
    q = "SELECT depth FROM artiqldb.word_folders WHERE id=%s"
    repl = execute_query(connection, q, (parent_id,))
    depth = repl.fetchall()
    if depth:
        depth = depth[0][0] + 1
    else:
        depth = 0
    q = "INSERT INTO artiqldb.word_folders (id, parent_id, user_id, depth, name) VALUES (uuid(), %s, %s, %s, %s)"
    execute_query(
        connection,
        q,
        (
            parent_id,
            user_id,
            depth,
            name,
        ),
    )
    connection.commit()


def is_word_unique_in_folder(connection, user_id, folder_id, word):
    q = "SELECT word FROM artiqldb.words as words INNER JOIN artiqldb.word_folder_words as fld ON fld.folder_id=%s AND words.id=fld.word_id AND words.word=%s AND fld.user_id=%s"
    repl = execute_query(
        connection,
        q,
        (
            folder_id,
            word,
            user_id,
        ),
    )
    res = repl.fetchall()
    if res:
        return False
    return True


def save_word_to_folder(connection, user_id, folder_id, word_id):
    q = "INSERT INTO artiqldb.word_folder_words (user_id, folder_id, word_id) VALUES (%s, %s, %s)"
    execute_query(
        connection,
        q,
        (
            user_id,
            folder_id,
            word_id,
        ),
    )
    connection.commit()


def get_parent_folder_by_id(connection, folder_id):
    q = "SELECT parent_id FROM artiqldb.word_folders WHERE id=%s"
    repl = execute_query(connection, q, (folder_id,))
    parent_id = repl.fetchone()[0]
    return parent_id


def get_all_words_by_user_id(connection, user_id):
    q = "SELECT * FROM artiqldb.words WHERE user_id=%s ORDER BY date DESC"
    repl = execute_query(connection, q, (user_id,))
    words = repl.fetchall()
    words_dict = []
    for element in words:
        word_info = {
            "id": element[0],
            "word": element[2],
            "definition": element[3],
            "translation": element[4],
            "date": element[5],
        }
        words_dict.append(word_info)
    return words_dict


def delete_words_by_ids(connection, user_id, word_ids):
    values = [f'"{value}"' for value in word_ids]
    delete_flashcards_on_word_delete_by_word_ids(connection, user_id, word_ids)
    q = f'DELETE FROM artiqldb.word_folder_words WHERE user_id=%s AND word_id IN ({", ".join(values)})'
    execute_query(connection, q, (user_id,))
    connection.commit()
    q = f'DELETE FROM artiqldb.words WHERE user_id=%s AND id IN ({", ".join(values)})'
    execute_query(connection, q, (user_id,))
    connection.commit()


def get_folders_by_user_id_and_folder_start(connection, user_id, folder_start):
    q = f"""SELECT *
        FROM artiqldb.word_folders
        WHERE name LIKE '{folder_start}%' AND user_id = %s"""
    repl = execute_query(connection, q, (user_id,))
    folders = repl.fetchall()
    folders_dict = []
    for element in folders:
        new_folder = {
            "id": element[0],
            "parent_id": element[1],
            "user_id": element[2],
            "depth": element[3],
            "name": element[4],
        }
        folders_dict.append(new_folder)
    return folders_dict


def get_word_folder_path_by_folder_id(connection, user_id, folder_id, depth, name):
    if depth == 0:
        return f"/{name}"
    path = ""
    while depth != -1:
        q = f"SELECT parent_id, depth, name FROM artiqldb.word_folders WHERE user_id=%s AND id=%s AND depth={depth}"
        repl = execute_query(connection, q, (user_id, folder_id))
        info = repl.fetchone()
        if info:
            folder_id, depth, name = info
            depth -= 1
            path = f"/{name}" + path
    return path


def get_words_from_word_folder_by_folder_id(connection, user_id, folder_id):
    q = "SELECT words.* FROM artiqldb.word_folder_words as fld INNER JOIN artiqldb.words as words ON fld.word_id = words.id AND fld.folder_id = %s AND fld.user_id=%s ORDER BY words.date DESC"
    repl = execute_query(
        connection,
        q,
        (
            folder_id,
            user_id,
        ),
    )
    words = repl.fetchall()
    words_dict = []
    for element in words:
        word_info = {
            "id": element[0],
            "word": element[2],
            "definition": element[3],
            "translation": element[4],
            "date": element[5],
        }
        words_dict.append(word_info)
    return words_dict


def delete_word_folders_by_id(connection, user_id, folder_ids):
    values = [f'"{value}"' for value in folder_ids]
    for folder_id in folder_ids:
        word_ids = get_all_words_in_folder_by_id(connection, user_id, folder_id)
        if not word_ids:
            word_ids = [""]
            form_word_ids = ['""']
        else:
            form_word_ids = [f'"{word}"' for word in word_ids]
        nested_folders = get_nested_word_folders_by_folder_id(
            connection, user_id, folder_id
        )
        if not nested_folders:
            nested_folders = [""]
            form_nested_folders = ['""']
        else:
            form_nested_folders = [f'"{value}"' for value in nested_folders]
        q = f'DELETE FROM artiqldb.word_folder_words WHERE user_id=%s AND word_id IN ({", ".join(form_word_ids)}) AND folder_id IN ({", ".join(form_nested_folders)})'
        execute_query(connection, q, (user_id,))
        connection.commit()
        q = f'DELETE FROM artiqldb.word_folders WHERE user_id=%s AND id IN ({", ".join(form_nested_folders)})'
        execute_query(connection, q, (user_id,))
        connection.commit()


def delete_words_from_word_folder_by_id(connection, user_id, folder_id, word_ids):
    values = [f'"{value}"' for value in word_ids]
    q = f'DELETE FROM artiqldb.word_folder_words WHERE folder_id=%s AND user_id=%s AND word_id IN ({", ".join(values)})'
    execute_query(
        connection,
        q,
        (
            folder_id,
            user_id,
        ),
    )
    connection.commit()


def get_word_folder_depth_and_name_by_folder_id(connection, user_id, folder_id):
    q = "SELECT depth, name FROM artiqldb.word_folders WHERE user_id=%s AND id=%s"
    repl = execute_query(
        connection,
        q,
        (
            user_id,
            folder_id,
        ),
    )
    res = repl.fetchall()[0]
    return res[0], res[1]


def update_word_definition_translation_by_word_id(
    connection, user_id, word_id, new_definition, new_translation
):
    q = """UPDATE artiqldb.words
    SET translation=%s, definition=%s
    WHERE id=%s AND user_id=%s
    """
    execute_query(connection, q, (new_translation, new_definition, word_id, user_id))
    connection.commit()


def get_nested_word_folders_by_folder_id(connection, user_id, folder_id):
    all_word_folders = []
    q = "SELECT id, parent_id FROM artiqldb.word_folders WHERE user_id=%s ORDER BY depth ASC"
    repl = execute_query(connection, q, (user_id,))
    all_word_folders = repl.fetchall()
    nested_folders = [folder_id]
    for element in all_word_folders:
        if element[1] in nested_folders:
            nested_folders.append(element[0])
    return nested_folders


def get_all_words_in_folder_by_id(connection, user_id, folder_id):
    folder_ids = get_nested_word_folders_by_folder_id(connection, user_id, folder_id)
    form_folder_ids = [f'"{value}"' for value in folder_ids]
    q = f"""SELECT words.id FROM
    artiqldb.word_folder_words as fld
    INNER JOIN
    artiqldb.words as words
    ON
    fld.word_id = words.id
    AND words.user_id = %s
    AND fld.folder_id IN ({", ".join(form_folder_ids)})
    """
    repl = execute_query(connection, q, (user_id,))
    res = repl.fetchall()
    word_ids = [el[0] for el in res]
    return word_ids


# WORKING WITH FLASHCARDS


def get_child_flashcard_folders_by_parent_id(connection, user_id, parent_id):
    q = "SELECT * FROM artiqldb.flashcard_folders WHERE parent_id=%s AND user_id=%s"
    repl = execute_query(
        connection,
        q,
        (
            parent_id,
            user_id,
        ),
    )
    folders = repl.fetchall()
    folders_dict = []
    for element in folders:
        new_folder = {
            "id": element[0],
            "parent_id": element[1],
            "user_id": element[2],
            "depth": element[3],
            "name": element[4],
        }
        folders_dict.append(new_folder)
    return folders_dict


def is_flashcard_folder_unique_by_parent_id(connection, user_id, parent_id, name):
    q = "SELECT id FROM artiqldb.flashcard_folders WHERE parent_id=%s AND name=%s AND user_id=%s"
    repl = execute_query(connection, q, (parent_id, name, user_id))
    res = repl.fetchall()
    if res:
        return False
    return True


def add_new_flashcard_folder(connection, parent_id, user_id, name):
    q = "SELECT depth FROM artiqldb.flashcard_folders WHERE id=%s"
    repl = execute_query(connection, q, (parent_id,))
    depth = repl.fetchall()
    if depth:
        depth = depth[0][0] + 1
    else:
        depth = 0
    q = "INSERT INTO artiqldb.flashcard_folders (id, parent_id, user_id, depth, name) VALUES (uuid(), %s, %s, %s, %s)"
    execute_query(
        connection,
        q,
        (
            parent_id,
            user_id,
            depth,
            name,
        ),
    )
    connection.commit()


def get_flashcard_parent_folder_by_id(connection, folder_id):
    q = "SELECT parent_id FROM artiqldb.flashcard_folders WHERE id=%s"
    repl = execute_query(connection, q, (folder_id,))
    parent_id = repl.fetchone()[0]
    return parent_id


def is_flashcard_unique_in_folder(connection, user_id, word_id, folder_id):
    q = """
    SELECT * FROM artiqldb.flashcard_folder_flashcards as fld
    INNER JOIN
    artiqldb.flashcards as flashcards
    ON flashcards.user_id=fld.user_id
    AND fld.user_id=%s
    AND fld.folder_id=%s
    AND flashcards.id=fld.flashcard_id
    WHERE flashcards.word_id=%s
    """
    repl = execute_query(
        connection,
        q,
        (
            user_id,
            folder_id,
            word_id,
        ),
    )
    res = repl.fetchall()
    if res:
        return False
    return True


def add_new_flashcard_to_folder_by_id(connection, user_id, word_id, type, folder_id):
    q = "SELECT uuid()"
    repl = execute_query(connection, q)
    flashcard_id = repl.fetchone()[0]
    q = "INSERT INTO artiqldb.flashcards (id, user_id, word_id, type) VALUES (%s, %s, %s, %s)"
    execute_query(
        connection,
        q,
        (
            flashcard_id,
            user_id,
            word_id,
            type,
        ),
    )
    connection.commit()
    q = "INSERT INTO artiqldb.flashcard_folder_flashcards (user_id, folder_id, flashcard_id) VALUES (%s, %s, %s)"
    execute_query(
        connection,
        q,
        (
            user_id,
            folder_id,
            flashcard_id,
        ),
    )
    connection.commit()


def get_all_flashcard_info_by_id(connection, user_id, flashcard_id):
    q = """SELECT flashcards.id, words.id, flashcards.type, words.word, words.definition, words.translation FROM artiqldb.flashcards AS flashcards
    INNER JOIN
    artiqldb.words as words
    ON
    flashcards.word_id=words.id
    WHERE flashcards.user_id=%s AND flashcards.id=%s
    """
    repl = execute_query(
        connection,
        q,
        (
            user_id,
            flashcard_id,
        ),
    )
    res = repl.fetchone()
    flashcard_info = {
        "id": res[0],
        "word_id": res[1],
        "fl_type": res[2],
        "word": res[3],
        "definition": res[4],
        "translation": res[5],
    }
    return flashcard_info


def get_flashcard_ids_from_folder_by_folder_id(connection, user_id, folder_id):
    q = "SELECT flashcard_id FROM artiqldb.flashcard_folder_flashcards WHERE user_id=%s AND folder_id=%s"
    repl = execute_query(
        connection,
        q,
        (
            user_id,
            folder_id,
        ),
    )
    res = repl.fetchall()
    flashcard_ids = [el[0] for el in res]
    return flashcard_ids


def delete_flashcards_on_word_delete_by_word_ids(connection, user_id, word_ids):
    word_ids = [f'"{value}"' for value in word_ids]
    q = f'SELECT id FROM artiqldb.flashcards WHERE user_id=%s AND word_id IN ({", ".join(word_ids)})'
    repl = execute_query(connection, q, (user_id,))
    if repl:
        flashcard_ids = repl.fetchall()
        flashcard_ids = [f'"{flashcard[0]}"' for flashcard in flashcard_ids]
        # deleting connections
        q = f'DELETE FROM artiqldb.flashcard_folder_flashcards WHERE user_id=%s AND flashcard_id IN ({", ".join(flashcard_ids)})'
        execute_query(connection, q, (user_id,))
        connection.commit()
        # deleting flashcards
        q = f'DELETE FROM artiqldb.flashcards WHERE user_id=%s AND id IN ({", ".join(flashcard_ids)})'
        execute_query(connection, q, (user_id,))
        connection.commit()
        delete_workouts_on_flashcard_delete_by_flashcard_ids(
            connection, user_id, flashcard_ids
        )


def delete_flashcard_folders_by_id(connection, user_id, folder_ids):
    form_folder_ids = [f'"{value}"' for value in folder_ids]
    for folder_id in folder_ids:
        # deleting flashcards from folders
        flashcard_ids = get_all_flashcards_in_folder_by_id(
            connection, user_id, folder_id
        )
        if not flashcard_ids:
            flashcard_ids = [""]
            form_flashcard_ids = ['""']
        else:
            form_flashcard_ids = [f'"{flashcard}"' for flashcard in flashcard_ids]
        q = f'DELETE FROM artiqldb.flashcards WHERE user_id=%s AND id IN ({", ".join(form_flashcard_ids)})'
        execute_query(connection, q, (user_id,))
        connection.commit()
        delete_workouts_on_flashcard_delete_by_flashcard_ids(
            connection, user_id, flashcard_ids
        )
        nested_folders = get_nested_flashcard_folders_by_folder_id(
            connection, user_id, folder_id
        )
        if not nested_folders:
            nested_folders = [""]
            form_nested_folders_ids = ['""']
        else:
            form_nested_folders_ids = [f'"{value}"' for value in nested_folders]
        # deleting folder connections and folders
        q = f'DELETE FROM artiqldb.flashcard_folder_flashcards WHERE user_id=%s AND folder_id IN ({", ".join(form_nested_folders_ids)})'
        execute_query(connection, q, (user_id,))
        connection.commit()
        q = f'DELETE FROM artiqldb.flashcard_folders WHERE user_id=%s AND id IN ({", ".join(form_nested_folders_ids)})'
        execute_query(connection, q, (user_id,))
        connection.commit()


def delete_flashcards_from_folder_by_id(connection, user_id, folder_id, flashcard_ids):
    form_flashcard_ids = [f'"{value}"' for value in flashcard_ids]
    q = f'DELETE FROM artiqldb.flashcard_folder_flashcards WHERE folder_id=%s AND user_id=%s AND flashcard_id IN ({", ".join(form_flashcard_ids)})'
    execute_query(
        connection,
        q,
        (
            folder_id,
            user_id,
        ),
    )
    connection.commit()
    q = f'DELETE FROM artiqldb.flashcards WHERE user_id=%s AND id IN ({", ".join(form_flashcard_ids)})'
    execute_query(connection, q, (user_id,))
    connection.commit()
    delete_workouts_on_flashcard_delete_by_flashcard_ids(
        connection, user_id, flashcard_ids
    )


def get_flashcard_folders_by_user_id_and_folder_contain(
    connection, user_id, folder_contain
):
    q = f'''SELECT *
        FROM artiqldb.flashcard_folders
        WHERE name LIKE "%{folder_contain}%" AND user_id = "{user_id}"'''
    repl = execute_query(connection, q)
    folders_dict = []
    if repl:
        folders = repl.fetchall()
        for element in folders:
            new_folder = {
                "id": element[0],
                "parent_id": element[1],
                "user_id": element[2],
                "depth": element[3],
                "name": element[4],
            }
            folders_dict.append(new_folder)
    return folders_dict


def get_flashcard_folder_path_by_folder_id(connection, user_id, folder_id, depth, name):
    if depth == 0:
        return f"/{name}"
    path = ""
    while depth != -1:
        q = f"SELECT parent_id, depth, name FROM artiqldb.flashcard_folders WHERE user_id=%s AND id=%s AND depth={depth}"
        repl = execute_query(connection, q, (user_id, folder_id))
        info = repl.fetchone()
        if info:
            folder_id, depth, name = info
            depth -= 1
            path = f"/{name}" + path
    return path


def get_flashcards_and_folder_ids_from_folders_by_user_id_and_flashcard_contain(
    connection, user_id, flashcard_contain
):
    q = f'''SELECT flashcard_folder_flashcards.folder_id, flashcards.id FROM artiqldb.words as words
    INNER JOIN artiqldb.flashcards as flashcards
    LEFT JOIN artiqldb.flashcard_folder_flashcards AS flashcard_folder_flashcards
    ON flashcards.id = flashcard_folder_flashcards.flashcard_id
    ON words.id = flashcards.word_id
    AND flashcards.user_id="{user_id}"
    AND words.word LIKE "%{flashcard_contain}%"'''
    repl = execute_query(connection, q)
    flashcards_info = []
    if repl:
        flashcards = repl.fetchall()
        for element in flashcards:
            flashcard_info = {"folder_id": element[0], "id": element[1]}
            flashcards_info.append(flashcard_info)
    return flashcards_info


def get_flashcard_folder_depth_and_name_by_folder_id(connection, user_id, folder_id):
    q = "SELECT depth, name FROM artiqldb.flashcard_folders WHERE user_id=%s AND id=%s"
    repl = execute_query(
        connection,
        q,
        (
            user_id,
            folder_id,
        ),
    )
    res = repl.fetchall()[0]
    return res[0], res[1]


def get_flashcard_parent_folder_by_id(connection, folder_id):
    q = "SELECT parent_id FROM artiqldb.flashcard_folders WHERE id=%s"
    repl = execute_query(connection, q, (folder_id,))
    parent_id = repl.fetchone()[0]
    return parent_id


def get_nested_flashcard_folders_by_folder_id(connection, user_id, folder_id):
    all_flashcard_folders = []
    q = "SELECT id, parent_id FROM artiqldb.flashcard_folders WHERE user_id=%s ORDER BY depth ASC"
    repl = execute_query(connection, q, (user_id,))
    all_flashcard_folders = repl.fetchall()
    nested_folders = [folder_id]
    for element in all_flashcard_folders:
        if element[1] in nested_folders:
            nested_folders.append(element[0])
    return nested_folders


def get_all_flashcards_in_folder_by_id(connection, user_id, folder_id):
    folder_ids = get_nested_flashcard_folders_by_folder_id(
        connection, user_id, folder_id
    )
    form_folder_ids = [f'"{value}"' for value in folder_ids]
    q = f"""SELECT flashcards.id FROM
    artiqldb.flashcard_folder_flashcards as fld
    INNER JOIN
    artiqldb.flashcards as flashcards
    ON
    fld.flashcard_id = flashcards.id
    AND flashcards.user_id = %s
    AND fld.folder_id IN ({", ".join(form_folder_ids)})
    """
    repl = execute_query(connection, q, (user_id,))
    res = repl.fetchall()
    flashcard_ids = [el[0] for el in res]
    return flashcard_ids


def get_all_unique_by_word_flashcards(connection, flashcard_ids):
    form_flashcard_ids = [f"'{value}'" for value in flashcard_ids]
    q = f"""
    SELECT
        flashcards.id
    FROM artiqldb.words AS words
    INNER JOIN artiqldb.flashcards AS flashcards
        INNER JOIN
        (SELECT
            artiqldb.words.id AS id,
            MAX(artiqldb.flashcards.type) AS maxtype
        FROM artiqldb.words
            INNER JOIN artiqldb.flashcards
            ON artiqldb.words.id = artiqldb.flashcards.word_id
            AND flashcards.id IN ({", ".join(form_flashcard_ids)})
                    GROUP BY artiqldb.words.id) AS wft
            ON flashcards.word_id = wft.id
        AND flashcards.type = wft.maxtype
    ON words.id = flashcards.word_id
    AND flashcards.id IN ({", ".join(form_flashcard_ids)})
    """
    repl = execute_query(connection, q)
    res = repl.fetchall()
    flashcard_ids = [el[0] for el in res]
    return flashcard_ids


# Working with workouts


def get_child_workout_folders_by_parent_id(connection, user_id, parent_id):
    q = "SELECT * FROM artiqldb.workout_folders WHERE parent_id=%s AND user_id=%s"
    repl = execute_query(
        connection,
        q,
        (
            parent_id,
            user_id,
        ),
    )
    folders = repl.fetchall()
    folders_dict = []
    for element in folders:
        new_folder = {
            "id": element[0],
            "parent_id": element[1],
            "user_id": element[2],
            "depth": element[3],
            "name": element[4],
        }
        folders_dict.append(new_folder)
    return folders_dict


def is_workout_folder_unique_by_parent_id(connection, user_id, parent_id, name):
    q = "SELECT id FROM artiqldb.workout_folders WHERE parent_id=%s AND name=%s AND user_id=%s"
    repl = execute_query(connection, q, (parent_id, name, user_id))
    res = repl.fetchall()
    if res:
        return False
    return True


def add_new_workout_folder(connection, user_id, parent_id, name):
    q = "SELECT depth FROM artiqldb.workout_folders WHERE id=%s"
    repl = execute_query(connection, q, (parent_id,))
    depth = repl.fetchall()
    if depth:
        depth = depth[0][0] + 1
    else:
        depth = 0
    q = "INSERT INTO artiqldb.workout_folders (id, parent_id, user_id, depth, name) VALUES (uuid(), %s, %s, %s, %s)"
    execute_query(
        connection,
        q,
        (
            parent_id,
            user_id,
            depth,
            name,
        ),
    )
    connection.commit()


def is_workout_name_unique_in_folder_id(connection, user_id, folder_id, name):
    q = """SELECT * FROM artiqldb.workout_folder_workouts as fld
    INNER JOIN
    artiqldb.workouts as workouts
    ON fld.workout_id=workouts.id
    AND fld.user_id=%s
    AND fld.folder_id=%s
    WHERE workouts.name=%s
    """
    repl = execute_query(
        connection,
        q,
        (
            user_id,
            folder_id,
            name,
        ),
    )
    res = repl.fetchall()
    if res:
        return False
    return True


def add_count_workout_to_folder_by_id(connection, user_id, folder_id, name, cnt):
    q = "SELECT uuid()"
    workout_id = execute_query(connection, q).fetchone()[0]
    q = "INSERT INTO artiqldb.workouts (id, user_id, type, name) VALUES (%s, %s, 1, %s)"
    execute_query(
        connection,
        q,
        (
            workout_id,
            user_id,
            name,
        ),
    )
    connection.commit()
    q = "INSERT INTO artiqldb.workouts_count (user_id, workout_id, cnt) VALUES (%s, %s, %s)"
    execute_query(
        connection,
        q,
        (
            user_id,
            workout_id,
            cnt,
        ),
    )
    connection.commit()
    q = "INSERT INTO artiqldb.workout_folder_workouts (user_id, folder_id, workout_id) VALUES (%s, %s, %s)"
    execute_query(
        connection,
        q,
        (
            user_id,
            folder_id,
            workout_id,
        ),
    )
    connection.commit()


def get_workout_parent_folder_by_id(connection, folder_id):
    q = "SELECT parent_id FROM artiqldb.workout_folders WHERE id=%s"
    repl = execute_query(connection, q, (folder_id,))
    parent_id = repl.fetchone()[0]
    return parent_id


def add_workout_with_flashcards_to_folder_by_id(
    connection, user_id, folder_id, name, flashcard_ids
):
    q = "SELECT uuid()"
    workout_id = execute_query(connection, q).fetchone()[0]
    q = "INSERT INTO artiqldb.workouts (id, user_id, type, name) VALUES (%s, %s, 2, %s)"
    execute_query(
        connection,
        q,
        (
            workout_id,
            user_id,
            name,
        ),
    )
    connection.commit()
    for flashcard_id in flashcard_ids:
        q = "INSERT INTO artiqldb.workout_flashcards (user_id, workout_id, flashcard_id) VALUES (%s, %s, %s)"
        execute_query(
            connection,
            q,
            (
                user_id,
                workout_id,
                flashcard_id,
            ),
        )
        connection.commit()
    q = "INSERT INTO artiqldb.workout_folder_workouts (user_id, folder_id, workout_id) VALUES (%s, %s, %s)"
    execute_query(
        connection,
        q,
        (
            user_id,
            folder_id,
            workout_id,
        ),
    )
    connection.commit()


def get_workout_ids_from_folder_by_folder_id(connection, user_id, folder_id):
    q = "SELECT workout_id FROM artiqldb.workout_folder_workouts WHERE user_id=%s AND folder_id=%s"
    repl = execute_query(
        connection,
        q,
        (
            user_id,
            folder_id,
        ),
    )
    res = repl.fetchall()
    workout_ids = [el[0] for el in res]
    return workout_ids


def get_all_workout_info_by_id(connection, user_id, workout_id):
    q = "SELECT name, type FROM artiqldb.workouts WHERE user_id=%s AND id=%s"
    repl = execute_query(
        connection,
        q,
        (
            user_id,
            workout_id,
        ),
    )
    name, workout_type = repl.fetchone()
    if workout_type == 1:
        q = "SELECT cnt FROM artiqldb.workouts_count WHERE user_id=%s AND workout_id=%s"
        repl = execute_query(
            connection,
            q,
            (
                user_id,
                workout_id,
            ),
        )
        cnt = repl.fetchone()[0]
        flashcard_ids = []
    else:
        q = "SELECT flashcard_id FROM artiqldb.workout_flashcards WHERE user_id=%s AND workout_id=%s"
        repl = execute_query(
            connection,
            q,
            (
                user_id,
                workout_id,
            ),
        )
        res = repl.fetchall()
        flashcard_ids = [el[0] for el in res]
        cnt = 0
    return {
        "name": name,
        "workout_type": workout_type,
        "flashcard_ids": flashcard_ids,
        "cnt": cnt,
    }


def delete_workouts_on_flashcard_delete_by_flashcard_ids(
    connection, user_id, flashcard_ids
):
    flashcard_ids = [f'"{value}"' for value in flashcard_ids]
    q = f'DELETE FROM artiqldb.workout_flashcards WHERE user_id=%s AND flashcard_id IN ({", ".join(flashcard_ids)})'
    execute_query(connection, q, (user_id,))
    connection.commit()


def get_nested_workout_folders_by_folder_id(connection, user_id, folder_id):
    all_workout_folders = []
    q = "SELECT id, parent_id FROM artiqldb.workout_folders WHERE user_id=%s ORDER BY depth ASC"
    repl = execute_query(connection, q, (user_id,))
    all_workout_folders = repl.fetchall()
    nested_folders = [folder_id]
    for element in all_workout_folders:
        if element[1] in nested_folders:
            nested_folders.append(element[0])
    return nested_folders


def get_all_workouts_in_folder_by_id(connection, user_id, folder_id):
    folder_ids = get_nested_workout_folders_by_folder_id(connection, user_id, folder_id)
    form_folder_ids = [f'"{value}"' for value in folder_ids]
    q = f"""SELECT workouts.id FROM
    artiqldb.workout_folder_workouts as fld
    INNER JOIN
    artiqldb.workouts as workouts
    ON
    fld.workout_id = workouts.id
    AND workouts.user_id = %s
    AND fld.folder_id IN ({", ".join(form_folder_ids)})
    """
    repl = execute_query(connection, q, (user_id,))
    res = repl.fetchall()
    workot_ids = [el[0] for el in res]
    return workot_ids


def delete_workout_folders_by_id(connection, user_id, folder_ids):
    form_folder_ids = [f'"{value}"' for value in folder_ids]
    for folder_id in folder_ids:
        # deleting workouts from folders
        workout_ids = get_all_workouts_in_folder_by_id(connection, user_id, folder_id)
        if not workout_ids:
            workout_ids = [""]
            form_workout_ids = ['""']
        else:
            form_workout_ids = [f'"{workout}"' for workout in workout_ids]
        q = f'DELETE FROM artiqldb.workouts_count WHERE user_id=%s AND workout_id IN ({", ".join(form_workout_ids)})'
        execute_query(connection, q, (user_id,))
        connection.commit()
        q = f'DELETE FROM artiqldb.workout_flashcards WHERE user_id=%s AND workout_id IN ({", ".join(form_workout_ids)})'
        execute_query(connection, q, (user_id,))
        connection.commit()
        q = f'DELETE FROM artiqldb.workouts WHERE user_id=%s AND id IN ({", ".join(form_workout_ids)})'
        execute_query(connection, q, (user_id,))
        connection.commit()
        nested_folders = get_nested_workout_folders_by_folder_id(
            connection, user_id, folder_id
        )
        if not nested_folders:
            nested_folders = [""]
            form_nested_folders_ids = ['""']
        else:
            form_nested_folders_ids = [f'"{value}"' for value in nested_folders]
        # deleting folder connections and folders
        q = f'DELETE FROM artiqldb.workout_folder_workouts WHERE user_id=%s AND folder_id IN ({", ".join(form_nested_folders_ids)})'
        execute_query(connection, q, (user_id,))
        connection.commit()
        q = f'DELETE FROM artiqldb.workout_folders WHERE user_id=%s AND id IN ({", ".join(form_nested_folders_ids)})'
        execute_query(connection, q, (user_id,))
        connection.commit()


def delete_workouts_from_folder_by_id(connection, user_id, folder_id, workout_ids):
    form_workout_ids = [f'"{value}"' for value in workout_ids]
    q = f'DELETE FROM artiqldb.workouts_count WHERE user_id=%s AND workout_id IN ({", ".join(form_workout_ids)})'
    execute_query(connection, q, (user_id,))
    connection.commit()
    q = f'DELETE FROM artiqldb.workout_flashcards WHERE user_id=%s AND workout_id IN ({", ".join(form_workout_ids)})'
    execute_query(connection, q, (user_id,))
    connection.commit()
    q = f'DELETE FROM artiqldb.workouts WHERE user_id=%s AND id IN ({", ".join(form_workout_ids)})'
    execute_query(connection, q, (user_id,))
    connection.commit()
    q = f'DELETE FROM artiqldb.workout_folder_workouts WHERE user_id=%s AND folder_id=%s AND workout_id IN ({", ".join(form_workout_ids)})'
    execute_query(
        connection,
        q,
        (
            user_id,
            folder_id,
        ),
    )
    connection.commit()


def get_workout_folders_by_user_id_and_folder_contain(
    connection, user_id, folder_contain
):
    q = f'''SELECT *
        FROM artiqldb.workout_folders
        WHERE name LIKE "%{folder_contain}%" AND user_id = "{user_id}"'''
    repl = execute_query(connection, q)
    folders_dict = []
    if repl:
        folders = repl.fetchall()
        for element in folders:
            new_folder = {
                "id": element[0],
                "parent_id": element[1],
                "user_id": element[2],
                "depth": element[3],
                "name": element[4],
            }
            folders_dict.append(new_folder)
    return folders_dict


def get_workouts_and_folder_ids_from_folders_by_user_id_and_workout_contain(
    connection, user_id, workout_contain
):
    q = f'''SELECT fld.folder_id, workouts.id FROM artiqldb.workout_folder_workouts as fld
    INNER JOIN artiqldb.workouts as workouts
    ON workouts.id = fld.workout_id
    AND fld.user_id = workouts.user_id
    AND workouts.user_id = "{user_id}"
    AND workouts.name LIKE "%{workout_contain}%"'''
    repl = execute_query(connection, q)
    workouts_info = []
    if repl:
        workouts = repl.fetchall()
        for element in workouts:
            workout_info = {"folder_id": element[0], "id": element[1]}
            workouts_info.append(workout_info)
    return workouts_info


def get_workout_folder_path_by_folder_id(connection, user_id, folder_id, depth, name):
    if depth == 0:
        return f"/{name}"
    path = ""
    while depth != -1:
        q = f"SELECT parent_id, depth, name FROM artiqldb.workout_folders WHERE user_id=%s AND id=%s AND depth={depth}"
        repl = execute_query(connection, q, (user_id, folder_id))
        info = repl.fetchone()
        if info:
            folder_id, depth, name = info
            depth -= 1
            path = f"/{name}" + path
    return path


def get_workout_folder_depth_and_name_by_folder_id(connection, user_id, folder_id):
    q = "SELECT depth, name FROM artiqldb.workout_folders WHERE user_id=%s AND id=%s"
    repl = execute_query(
        connection,
        q,
        (
            user_id,
            folder_id,
        ),
    )
    res = repl.fetchall()[0]
    return res[0], res[1]


def get_workout_parent_folder_by_id(connection, folder_id):
    q = "SELECT parent_id FROM artiqldb.workout_folders WHERE id=%s"
    repl = execute_query(connection, q, (folder_id,))
    parent_id = repl.fetchone()[0]
    return parent_id


def get_all_unique_by_word_flashcards_by_user_id(connection, user_id):
    q = f"""
    SELECT
        flashcards.id
    FROM artiqldb.words AS words
    INNER JOIN artiqldb.flashcards AS flashcards
        INNER JOIN
        (SELECT
            artiqldb.words.id AS id,
            MAX(artiqldb.flashcards.type) AS maxtype
        FROM artiqldb.words
            INNER JOIN artiqldb.flashcards
            ON artiqldb.words.id = artiqldb.flashcards.word_id
            AND flashcards.user_id = %s
                    GROUP BY artiqldb.words.id) AS wft
            ON flashcards.word_id = wft.id
        AND flashcards.type = wft.maxtype
    ON words.id = flashcards.word_id
    AND flashcards.user_id = %s
    """
    repl = execute_query(
        connection,
        q,
        (
            user_id,
            user_id,
        ),
    )
    res = repl.fetchall()
    flashcard_ids = [el[0] for el in res]
    return flashcard_ids


# working with user statistics


def add_completed_workout_info(
    connection,
    user_id,
    workout_start,
    workout_end,
    questions_number,
    answers_number,
    correct_answers_number,
):
    q = "INSERT INTO artiqldb.user_statistics (user_id, workout_start, workout_end, questions_number, answers_number, correct_answers_number) VALUES (%s, %s, %s, %s, %s, %s)"
    execute_query(
        connection,
        q,
        (
            user_id,
            workout_start,
            workout_end,
            questions_number,
            answers_number,
            correct_answers_number,
        ),
    )
    connection.commit()


def get_user_stats_by_time_range(connection, user_id, start_time, end_time):
    q = """
    SELECT
    COUNT(
    CASE WHEN user_statistics.questions_number = 0
        THEN 0
        ELSE user_statistics.completed_workout_id * user_statistics.answers_number/user_statistics.questions_number
        END) AS workout_count,
    SUM(user_statistics.workout_end - user_statistics.workout_start) AS time_count,
    SUM(user_statistics.correct_answers_number) AS correct_answers_count
    FROM
    artiqldb.user_statistics AS user_statistics
    WHERE
    user_statistics.user_id = %s
        AND user_statistics.workout_start >= %s
        AND user_statistics.workout_end <= %s
    """
    repl = execute_query(
        connection,
        q,
        (
            user_id,
            start_time,
            end_time,
        ),
    )
    res = repl.fetchall()
    workouts_count = res[0][0] if res[0][0] is not None else 0
    time_training_seconds = res[0][1] if res[0][1] is not None else 0
    correct_answers = res[0][2] if res[0][2] is not None else 0
    return {
        "workouts_count": workouts_count,
        "time_training_seconds": time_training_seconds,
        "correct_answers": correct_answers,
    }
