import mysql.connector
from utils.auxillary_functions import hash_password
from utils.auxillary_functions import get_cur_time_str
from classes.word import Word

# Function to establish a database connection
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='!Monkey10287',
            database='artiqldb'
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# Function to execute a SQL query
def execute_query(connection, query, params=None):
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        return cursor
    except Exception as e:
        print(f"Error executing SQL query: {e}")
        return None
    
# Working with artiqldb functions
def search_bar_server(connection, text, category):
    # getting all article ids with this category
    text = text.lower()
    heading_articles = []
    tag_articles = []
    q = 'SELECT id FROM artiqldb.tags WHERE name=%s'
    repl = execute_query(connection, q, (category,))
    tag_id = repl.fetchone()[0]

    q = 'SELECT article_id FROM artiqldb.articles_tags WHERE tag_id=%s'
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
            q = 'SELECT tag_id FROM artiqldb.articles_tags WHERE article_id=%s'
            repl = execute_query(connection, q, (cur_article_id,))
            tag_ids = repl.fetchall()
            for tag_id_info in tag_ids:
                tag_id = tag_id_info[0]
                q = 'SELECT name FROM artiqldb.tags WHERE id=%s'
                repl = execute_query(connection, q, (tag_id,))
                name = repl.fetchone()[0]
                if text in name:
                    tag_articles.append(cur_article_id)
    return heading_articles + tag_articles


def get_articles(connection, cnt):
    q = 'SELECT * FROM artiqldb.articles'
    repl = execute_query(connection, q)
    articles = repl.fetchall()[:cnt]
    return articles

def get_articles_by_tag(connection, tag):
    # getting id of the tag
    q = 'SELECT id FROM artiqldb.tags WHERE name=%s'
    repl = execute_query(connection, q, (tag,))
    tag_id = repl.fetchone()[0]

    # getting ids of the articles with that tag_id
    q = 'SELECT article_id FROM artiqldb.articles_tags WHERE tag_id=%s'
    repl = execute_query(connection, q, (tag_id,))
    article_ids = repl.fetchall()
    article_ids = [article_id[0] for article_id in article_ids]

    return article_ids

def get_article_by_id(connection, article_id):
    q = 'SELECT * FROM artiqldb.articles WHERE id=%s'
    repl = execute_query(connection, q, (article_id,))
    article = repl.fetchall()[0]
    return article

def get_article_id_by_heading(connection, heading):
    q = 'SELECT id FROM artiqldb.articles WHERE heading=%s'
    repl = execute_query(connection, q, (heading,))
    article_id = repl.fetchone()[0]
    return article_id

def get_main_heading_info_by_article_id(connection, article_id):
    # getting the first element of the article a.k.a. main_heading either with or without comment (summary)
    q = 'SELECT * FROM artiqldb.articles_elements WHERE article_id=%s ORDER BY `order`'
    repl = execute_query(connection, q, (article_id,))
    first_article_element = repl.fetchall()[0]
    element_type_id = first_article_element[1]
    element_id = first_article_element[2]

    # getting the name of the element_type by element_type_id
    q = 'SELECT name FROM artiqldb.element_type WHERE id=%s'
    repl = execute_query(connection, q, (element_type_id,))
    element_type = repl.fetchone()[0]
    
    return (element_type, element_type_id, element_id)

def get_main_heading_comment_by_element_id(connection, element_name, element_id):
    table_name = 'element_' + element_name
    q = f'SELECT comment FROM artiqldb.{table_name} WHERE id=%s'
    repl = execute_query(connection, q, (element_id,))
    comment = repl.fetchone()[0]
    return comment

def is_username_unique(connection, username):
    q = f'SELECT username FROM artiqldb.users WHERE username=%s'
    repl = execute_query(connection, q, (username,))
    res = repl.fetchall()
    if len(res) == 0:
        return True
    else:
        return False
    
def is_email_unique(connection, email):
    q = f'SELECT email FROM artiqldb.users WHERE email=%s'
    repl = execute_query(connection, q, (email,))
    res = repl.fetchall()
    if len(res) == 0:
        return True
    else:
        return False
    
def create_user(connection, username, email, password):
    q = f"INSERT INTO artiqldb.users (id, username, email, password) VALUE (uuid(), %s, %s, %s)"
    hashed_password = hash_password(password)
    execute_query(connection, q, (username, email, hashed_password,))
    connection.commit()

def create_user_registration_date(connection, username):
    q = f'SELECT id FROM artiqldb.users WHERE username=%s'
    repl = execute_query(connection, q, (username,))
    user_id = repl.fetchone()[0]
    q = f'INSERT INTO artiqldb.users_registration_date (user_id, date) VALUE (%s, %s)'
    date = get_cur_time_str()
    execute_query(connection, q, (user_id, date,))
    connection.commit()

def get_user_id_by_email(connection, email):
    q = 'SELECT * FROM artiqldb.users WHERE email=%s'
    repl = execute_query(connection, q, (email,))
    try:
        user_id = repl.fetchone()[0]
        return user_id
    except Exception:
        return -1

def get_password_by_user_id(connection, user_id):
    q = 'SELECT password FROM artiqldb.users WHERE id=%s'
    repl = execute_query(connection, q, (user_id,))
    password = repl.fetchone()[0]
    return password

def get_all_info_by_user_id(connection, user_id):
    q = 'SELECT * FROM artiqldb.users WHERE id=%s'
    repl = execute_query(connection, q, (user_id,))
    basic_info = repl.fetchone()[1:]
    q = 'SELECT date FROM artiqldb.users_registration_date WHERE user_id=%s'
    repl = execute_query(connection, q, (user_id,))
    registration_date = repl.fetchone()[0]
    return {'username': basic_info[0], 'email': basic_info[1], 'registration_date': registration_date}

def get_article_elements(connection, article_id):
    q = 'SELECT element_type_id, element_id, `order` FROM artiqldb.articles_elements WHERE article_id=%s ORDER BY `order` ASC'
    repl = execute_query(connection, q, (article_id,))
    all_elements = repl.fetchall()
    return all_elements

def get_element_info(connection, element_type_id, element_id):
    # getting the name of the element type with that id
    q = 'SELECT name FROM artiqldb.element_type WHERE id=%s'
    repl = execute_query(connection, q, (element_type_id,))
    element_class_name = repl.fetchone()[0]
    # getting the element with cur element_id and cur element_class_name
    q = f'SELECT * FROM artiqldb.element_{element_class_name} WHERE id=%s'
    repl = execute_query(connection, q, (element_id,))
    element_info = repl.fetchone()
    # getting the names of the columns
    q = f'SHOW COLUMNS FROM artiqldb.element_{element_class_name}'
    repl = execute_query(connection, q)
    all_columns = repl.fetchall()
    column_names = [column[0] for column in all_columns]
    # creating a dict column_name -> column_value
    dict_element_info = {'element_class_name': element_class_name}
    for i in range(len(column_names)):
        dict_element_info[column_names[i]] = element_info[i]
    return dict_element_info

# WORKING WITH WORDS
def is_word_already_saved(connection, user_id, word:Word):
    q = 'SELECT id FROM artiqldb.words WHERE user_id=%s AND word=%s'
    repl = execute_query(connection, q, (user_id, word.word,))
    res = repl.fetchall()
    if len(res) != 0:
        return True
    return False

def get_word_id_by_user_id_and_word(connection, user_id, word):
    q = 'SELECT id FROM artiqldb.words WHERE user_id=%s AND word=%s'
    repl = execute_query(connection, q, (user_id, word,))
    word_id = repl.fetchone()[0]
    return word_id

def get_word_id_by_user_id_and_word_start(connection, user_id, word_start):
    q = f'''SELECT * 
        FROM artiqldb.words
        WHERE word LIKE '{word_start}%' AND user_id = %s
        ORDER BY date DESC'''
    repl = execute_query(connection, q, (user_id,))
    words = repl.fetchall()
    words_dict = []
    for element in words:
        word_info = {'id': element[0], 'word': element[2], 'definition': element[3], 'translation': element[4], 'date': element[5]}
        words_dict.append(word_info)
    return words_dict

def fast_save_word(connection, user_id, word:Word, date):
    q = 'INSERT INTO artiqldb.words (id, user_id, word, definition, translation, date) VALUES (uuid(), %s, %s, %s, %s, %s)'
    execute_query(connection, q, (user_id, word.word, word.definition, word.translation, date,))
    connection.commit()

def get_child_folders_by_parent_id(connection, user_id, parent_id):
    q = 'SELECT * FROM artiqldb.word_folders WHERE parent_id=%s AND user_id=%s ORDER BY name ASC'
    repl = execute_query(connection, q, (parent_id, user_id,))
    folders = repl.fetchall()
    folders_dict = []
    for element in folders:
        new_folder = {'id': element[0], 'parent_id': element[1], 'user_id': element[2], 'depth': element[3], 'name': element[4]}
        folders_dict.append(new_folder)
    return folders_dict

def get_only_words_from_folder_by_id(connection, user_id, folder_id):
    q = 'SELECT words.word FROM artiqldb.word_folder_words as fld INNER JOIN artiqldb.words as words ON fld.word_id =  words.id AND fld.folder_id = %s AND fld.user_id=%s ORDER BY words.date DESC'
    repl = execute_query(connection, q, (folder_id, user_id,))
    words = repl.fetchall()
    return words

def is_unique_folder_by_parent_id(connection, parent_id, name):
    q = 'SELECT * FROM artiqldb.word_folders WHERE parent_id=%s AND name=%s'
    repl = execute_query(connection, q, (parent_id, name))
    names = repl.fetchall()
    if names:
        return False
    return True

def add_new_folder(connection, parent_id, user_id, name):
    q = 'SELECT depth FROM artiqldb.word_folders WHERE id=%s'
    repl = execute_query(connection, q, (parent_id,))
    depth = repl.fetchone()
    if depth:
        depth = depth[0]
        depth += 1
    else:
        depth = 0
    q = 'INSERT INTO artiqldb.word_folders (id, parent_id, user_id, depth, name) VALUES (uuid(), %s, %s, %s, %s)'
    execute_query(connection, q, (parent_id, user_id, depth, name,))
    connection.commit()

def is_word_unique_in_folder(connection, folder_id, word):
    q = 'SELECT word FROM artiqldb.words as words INNER JOIN artiqldb.word_folder_words as fld ON fld.folder_id=%s AND words.id=fld.word_id AND words.word=%s'
    repl = execute_query(connection, q, (folder_id, word,))
    words = repl.fetchall()
    if words:
        return False
    return True

def save_word_to_folder(connection, user_id, folder_id, word_id):
    q = 'INSERT INTO artiqldb.word_folder_words (user_id, folder_id, word_id) VALUES (%s, %s, %s)'
    execute_query(connection, q, (user_id, folder_id, word_id,))
    connection.commit()

def get_parent_folder_by_id(connection, folder_id):
    q = 'SELECT parent_id FROM artiqldb.word_folders WHERE id=%s'
    repl = execute_query(connection, q, (folder_id,))
    parent_id = repl.fetchone()[0]
    return parent_id

def get_folder_name_by_id(connection, folder_id):
    q = 'SELECT name FROM artiqldb.word_folders WHERE id=%s'
    repl = execute_query(connection, q, (folder_id,))
    name = repl.fetchone()[0]
    return name

def get_all_words_by_user_id(connection, user_id):
    q = 'SELECT * FROM artiqldb.words WHERE user_id=%s ORDER BY date DESC'
    repl = execute_query(connection, q, (user_id,))
    words = repl.fetchall()
    words_dict = []
    for element in words:
        word_info = {'id': element[0], 'word': element[2], 'definition': element[3], 'translation': element[4], 'date': element[5]}
        words_dict.append(word_info)
    return words_dict

def delete_words_by_ids(connection, word_ids):
    values = [f'"{value}"' for value in word_ids]
    q = f'DELETE FROM artiqldb.word_folder_words WHERE word_id IN ({", ".join(values)})'
    execute_query(connection, q)
    connection.commit()
    q = f'DELETE FROM artiqldb.words WHERE id IN ({", ".join(values)})'
    execute_query(connection, q)
    connection.commit()
