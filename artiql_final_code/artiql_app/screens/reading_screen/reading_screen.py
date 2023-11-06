from kivymd.uix.screen import MDScreen
from kivy.app import App
from kivymd.uix.button import MDIconButton
from kivymd.uix.relativelayout import MDRelativeLayout
import utils.db_functions as db
import utils.auxillary_functions as aux
import utils.definitions_api as def_api
from components.element_paragraph.element_paragraph import ElementParagraph
from components.element_main_heading_comment_image.element_main_heading_comment_image import ElementMainHeadingCommentImage
from components.element_main_heading_comment_image_with_comment.element_main_heading_comment_image_with_comment import ElementMainHeadingCommentImageWithComment
from components.element_image_comment_author.element_image_comment_author import ElementImageCommentAuthor
from components.element_image_author.element_image_author import ElementImageAuthor
from components.element_image_no_comment.element_image_no_comment import ElementImageNoComment
import utils.yandex_translate_functions as ya_translate
from kivy.animation import Animation
from components.translation_definition_div.translation_definition_div import TranslationDefinitionDiv
from kivy.uix.scrollview import ScrollView
from kivymd.uix.label import MDLabel
from components.definition_card_part_of_speech_label.definition_card_part_of_speech_label import DefinitionCardPartOfSpeechLabel
from components.definition_card_phonetic_label.definition_card_phonetic_label import DefinitionCardPhoneticLabel
from components.definition_card_definition_label.definition_card_definition_label import DefinitionCardDefinitionLabel
from components.definition_card_not_found_label.definition_card_not_found_label import DefinitionCardNotFoundLabel
import threading
from kivy.clock import mainthread
from kivy.clock import Clock


class ReadingScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.app = App.get_running_app()
        self.text_in_english = ""
        self.russian_translation = ""
        self.english_definition = ""
        self.active_text_input = ""
        self.is_card_active = False

    def on_touch_down(self, touch):
        if self.collide_point(
                touch.x, touch.y) and touch.y > self.height * 0.3:
            return super().on_touch_down(touch)
        elif self.is_card_active and self.collide_point(touch.x, touch.y) and touch.y <= self.height * 0.3:
            self.translation_div.on_touch_down(touch)
        else:
            return super().on_touch_down(touch)

    def update_definition_card_process(self, text):
        process = threading.Thread(
            target=self.update_definition_card, args=(text,))
        process.start()

    def update_definition_card(self, text):
        self.text_in_english = text
        definitions_info = def_api.get_definitions(text)
        Clock.schedule_once(
            lambda dt: self.update_definition_card_ui(definitions_info))

    def update_definition_card_ui(self, definitions_info):
        scroll_view_layout = self.translation_div.ids.definition_scroll_view_layout
        delete_children = scroll_view_layout.children[::]
        for child in delete_children:
            if child.__class__.__name__ == 'MDLabel' and child.text == 'Loading...':
                scroll_view_layout.remove_widget(child)
        cur_definition = ''
        if definitions_info == -1:
            scroll_view_layout.add_widget(DefinitionCardNotFoundLabel())
            cur_definition = "Definition not found"
        else:
            if definitions_info.get('phonetic') != '':
                formated_phonetic = definitions_info['phonetic'][1:-1]
                scroll_view_layout.add_widget(
                    DefinitionCardPhoneticLabel(
                        phonetic=formated_phonetic))
            for meaning in definitions_info['meanings']:
                scroll_view_layout.add_widget(
                    DefinitionCardPartOfSpeechLabel(
                        part_of_speech=meaning['part_of_speech']))
                cur_definition += f'{meaning["part_of_speech"]}\n'
                cnt = 1
                for definition in meaning['definitions']:
                    scroll_view_layout.add_widget(
                        DefinitionCardDefinitionLabel(
                            cnt=cnt, definition_text=definition))
                    cur_definition += f'{cnt}. {definition}\n'
                    cnt += 1
        self.english_definition = cur_definition

    def update_translation_card_process(self, text):
        process = threading.Thread(
            target=self.update_translation_card, args=(text,))
        process.start()

    def update_translation_card(self, text):
        self.text_in_english = text
        russian_text = ya_translate.translate_to_russian(text, self.ima_token)
        if russian_text != -1:
            self.russian_translation = russian_text
            self.translation_div.ids.russian_translation.text = russian_text
        else:
            self.translation_div.ids.russian_translation.text = 'Oops! Something went wrong'

    def prepare_cards(self, text):
        translation_div = self.translation_div
        translation_div.ids.russian_translation.text = 'Loading...'
        translation_div.ids.definition_input.text = text
        translation_div.ids.translation_input.text = text
        scroll_view_layout = self.translation_div.ids.definition_scroll_view_layout
        delete_children = scroll_view_layout.children[::]
        for child in delete_children:
            if child.__class__.__name__ != 'MDLabel':
                scroll_view_layout.remove_widget(child)
        scroll_view_layout.add_widget(
            MDLabel(
                text='Loading...',
                font_name='fonts/Helvetica',
                theme_text_color='Custom',
                text_color='black',
                adaptive_height=True))

    @mainthread
    def slide_translation_card_up(self, text, active_text_input):
        self.is_card_active = True
        self.active_text_input = active_text_input
        translation_div = self.translation_div
        if self.text_in_english != text:
            self.prepare_cards(text)
        anim = Animation(
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.15},
            duration=0.3)
        anim.start(translation_div.ids.translation_card)
        if self.text_in_english != text:
            self.russian_translation = '-1'
            self.english_definition = '-1'
            self.update_translation_card_process(text)
            self.update_definition_card_process(text)
            self.text_in_english = text
            translation_div.ids.definition_scroll_view.scroll_y = 1
            translation_div.ids.translation_card_screen_manager.transition.direction = 'right'
            translation_div.ids.translation_card_screen_manager.current = 'definition_screen'
            translation_div.ids.previous_screen.opacity = 0
            translation_div.ids.next_screen.opacity = 1
        Clock.schedule_once(
            lambda dt: setattr(
                self.active_text_input,
                'focus',
                False),
            2)

    def slide_translation_card_down(self):
        anim = Animation(
            pos_hint={
                "center_x": 0.5,
                "center_y": -0.16},
            duration=0.3)
        anim.start(self.translation_div.ids.translation_card)
        Clock.schedule_once(
            lambda dt: setattr(
                self.active_text_input,
                'focus',
                False),
            0)
        self.is_card_active = False

    def add_element_image_no_comment(self, element_info):
        self.reading_scroll_view.add_widget(
            ElementImageNoComment(
                image=element_info['image']))

    def add_element_image_author(self, element_info):
        self.reading_scroll_view.add_widget(
            ElementImageAuthor(
                image=element_info['image'],
                author=element_info['author']))

    def add_element_image_comment_author(self, element_info):
        self.reading_scroll_view.add_widget(
            ElementImageCommentAuthor(
                image=element_info['image'],
                author=element_info['author'],
                comment=element_info['comment']))

    def add_element_main_heading_comment_image_with_comment(
            self, element_info):
        d = str(element_info['date'].strftime('%Y-%m-%d'))
        article_date = aux.formate_date(d)
        self.reading_scroll_view.add_widget(
            ElementMainHeadingCommentImageWithComment(
                source=element_info['source'],
                heading_text=element_info['heading'],
                author=element_info['author'],
                date=article_date,
                comment=element_info['comment'],
                image=element_info['image'],
                image_source=element_info['image_source'],
                image_comment=element_info['image_comment']))

    def add_element_main_heading_comment_image(self, element_info):
        d = str(element_info['date'].strftime('%Y-%m-%d'))
        article_date = aux.formate_date(d)
        self.reading_scroll_view.add_widget(
            ElementMainHeadingCommentImage(
                source=element_info['source'],
                heading_text=element_info['heading'],
                author=element_info['author'],
                date=article_date,
                comment=element_info['comment'],
                image=element_info['image'],
                image_source=element_info['image_source']))

    def add_element_paragraph(self, element_info):
        new_el = ElementParagraph(input_text=element_info['text'])
        self.reading_scroll_view.add_widget(new_el)

    def add_elements_process(self, article_heading):
        process = threading.Thread(
            target=self.get_elements_function, args=(
                article_heading,))
        process.start()

    @mainthread
    def start_adding_elements(self, article_heading):
        root = App.get_running_app().root
        catalog_screen_manager = root.ids.catalog_screen_manager
        catalog_screen_manager.transition.direction = 'left'
        catalog_screen_manager.current = 'loading_screen'
        self.add_elements_process(article_heading)

    def add_elements_ui(self, elements_info):
        self.reading_scroll_view = self.ids.reading_scroll_view
        self.reading_scroll_view.clear_widgets()
        if len(self.children) > 2:
            children = self.children[::-1]
            for child in children:
                if child.__class__.__name__ == 'TranslationDefinitionDiv':
                    self.remove_widget(child)
                    break
        button_layout = MDRelativeLayout(size_hint_y=None, height=1)
        button_layout.add_widget(BackButton(pos=(-15, -20)))
        self.reading_scroll_view.add_widget(button_layout)
        interval = 0.2
        for element_info in elements_info:
            if element_info['element_class_name'] == 'paragraph':
                Clock.schedule_once(
                    lambda dt,
                    element_info=element_info: self.add_element_paragraph(element_info),
                    interval)
            elif element_info['element_class_name'] == 'main_heading_comment_image':
                Clock.schedule_once(
                    lambda dt,
                    element_info=element_info: self.add_element_main_heading_comment_image(element_info),
                    interval)
            elif element_info['element_class_name'] == 'main_heading_comment_image_with_comment':
                Clock.schedule_once(
                    lambda dt,
                    element_info=element_info: self.add_element_main_heading_comment_image_with_comment(element_info),
                    interval)
            elif element_info['element_class_name'] == 'image_comment_author':
                Clock.schedule_once(
                    lambda dt,
                    element_info=element_info: self.add_element_image_comment_author(element_info),
                    interval)
            elif element_info['element_class_name'] == 'image_author':
                Clock.schedule_once(
                    lambda dt,
                    element_info=element_info: self.add_element_image_author(element_info),
                    interval)
            elif element_info['element_class_name'] == 'image_no_comment':
                Clock.schedule_once(
                    lambda dt,
                    element_info=element_info: self.add_element_image_no_comment(element_info),
                    interval)
            interval += 0.05
        self.translation_div = TranslationDefinitionDiv()
        Clock.schedule_once(lambda dt: self.add_widget(self.translation_div))
        Clock.schedule_once(
            lambda dt: self.transition_to_reading_screen(),
            interval + 0.4)

    def get_elements_function(self, article_heading):
        self.db_connection = self.app.root.db_connection
        self.ima_token, self.ya_expires_at = ya_translate.get_IAM_token()
        article_id = db.get_article_id_by_heading(
            self.db_connection, article_heading)
        article_elements = db.get_article_elements(
            self.db_connection, article_id)
        elements_info = []
        for element in article_elements:
            element_info = db.get_element_info(
                self.db_connection, element[0], element[1])
            elements_info.append(element_info)
        Clock.schedule_once(
            lambda dt: self.add_elements_ui(elements_info), 0.05)

    def transition_to_reading_screen(self):
        root = App.get_running_app().root
        catalog_screen_manager = root.ids.catalog_screen_manager
        catalog_screen_manager.transition.direction = 'left'
        catalog_screen_manager.current = 'reading_screen'


class BackButton(MDIconButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def transition_to_category_search_screen(self):
        root = App.get_running_app().root
        root.ids.catalog_screen_manager.current = 'catalog_screen_search'
        root.ids.catalog_screen_manager.transition.direction = 'right'


class ReadingScrollView(ScrollView):
    def on_scroll_start(self, touch, check_children=True):
        root = App.get_running_app().root
        reading_screen = root.ids.reading_screen
        if self.collide_point(
                touch.x, touch.y) and touch.y > self.height * 0.3:
            return super().on_scroll_start(touch, check_children)
        elif reading_screen.is_card_active and self.collide_point(touch.x, touch.y) and touch.y <= self.height * 0.3:
            return
        else:
            return super().on_scroll_start(touch, check_children)
