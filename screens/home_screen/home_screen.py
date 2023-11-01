from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.swiper import MDSwiperItem
from kivymd.uix.behaviors import CommonElevationBehavior
from kivy.properties import StringProperty
from kivy.app import App
import utils.db_functions as db
import utils.auxillary_functions as aux


class HomeScreen(MDBottomNavigationItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_in_progress_articles(self):
        app_root = App.get_running_app().root
        self.db_connection = app_root.db_connection
        articles = db.get_articles(self.db_connection, 5)
        swiper = self.ids.swiper_widget
        for article in articles[::-1]:
            article_heading = article[1]
            article_author = article[2]
            d = str(article[3].strftime('%Y-%m-%d'))
            article_date = aux.formate_date(d)
            article_source = article[4].upper()
            article_link = article[5]
            article_image = article[6]
            print(article_image)

            swiper.add_widget(ArticleSwiperItem(heading=article_heading, image=article_image, source=article_source, date=article_date, author=article_author))
            print('Added')

class ArticleSwiperItem(MDSwiperItem, CommonElevationBehavior):
    heading = StringProperty()
    image = StringProperty()
    source = StringProperty()
    date = StringProperty()
    author = StringProperty()
