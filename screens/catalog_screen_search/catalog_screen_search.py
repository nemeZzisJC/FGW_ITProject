from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivymd.uix.card import MDCard
from kivy.app import App
import utils.db_functions as db
import utils.auxillary_functions as aux
from components.article_catalog_div.article_catalog_div import ArticleCatalogDiv


class CatalogSearch(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def search_bar_hint_text_color(self):
        search_bar = self.ids.catalog_search_bar
        if search_bar.text != "":
            self.ids.catalog_search_bar.hint_text_color_normal = [1, 1, 1, 0]
        else:
            self.ids.catalog_search_bar.hint_text_color_normal = 'lightgrey'
        search_bar.set_hint_text_color(search_bar.focus)

    def add_catalog_articles(self, article_ids):
        scroll_view = self.ids.catalog_scroll_view
        scroll_view.clear_widgets()
        for article_id in article_ids:
            article = db.get_article_by_id(self.db_connection, article_id)
            article_heading = article[1]
            article_author = article[2]
            d = str(article[3].strftime('%Y-%m-%d'))
            article_date = aux.formate_date(d)
            article_source = article[4].upper()
            article_link = article[5]
            article_image = article[6]
            # getting a comment of the article
            main_heading_info = db.get_main_heading_info_by_article_id(self.db_connection, article_id)
            if main_heading_info[0] in ('main_heading_comment_image_with_comment', 'main_heading_comment_image'):
                comment = db.get_main_heading_comment_by_element_id(self.db_connection, main_heading_info[0], main_heading_info[2])

            scroll_view.add_widget(ArticleCatalogDiv(heading=article_heading, image=article_image, source=article_source, date=article_date, author=article_author, comment=comment))

    def search_bar_response(self, text):
        root = App.get_running_app().root
        self.db_connection = root.db_connection
        article_ids = db.search_bar_server(self.db_connection, text, root.category)
        self.add_catalog_articles(article_ids)

    def transition_to_category_catalog(self):
        root = App.get_running_app().root
        root.ids.catalog_screen_manager.current = 'catalog_screen_category'
        root.ids.catalog_screen_manager.transition.direction = 'right'
        self.ids.catalog_search_bar.text = ""
