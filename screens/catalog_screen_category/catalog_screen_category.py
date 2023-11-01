from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.app import App
from components.article_catalog_div.article_catalog_div import ArticleCatalogDiv
import utils.db_functions as db
import utils.auxillary_functions as aux


class CatalogCategory(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def transition_to_search_catalog(self, category):
        root = App.get_running_app().root
        self.db_connection = root.db_connection
        root.category = category
        real_scroll_view = root.ids.catalog_search.ids.real_catalog_scroll_view
        root.ids.catalog_screen_manager.current = 'catalog_screen_search'
        root.ids.catalog_screen_manager.transition.direction = 'left'
        article_ids = db.get_articles_by_tag(self.db_connection, root.category)
        article_ids = aux.shuffle_article_ids(article_ids)
        self.add_catalog_articles(article_ids)
        real_scroll_view.scroll_y = 1

    def add_catalog_articles(self, article_ids):
        root = App.get_running_app().root
        scroll_view = root.ids.catalog_search.ids.catalog_scroll_view
        scroll_view.clear_widgets()
        cnt = 0
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

            scroll_view.add_widget(ArticleCatalogDiv(heading=article_heading, image=article_image, source=article_source, date=article_date, author=article_author, comment=comment, id=f'article_div{cnt}'))
            cnt += 1
