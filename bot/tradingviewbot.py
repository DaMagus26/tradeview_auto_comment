import logging
import random
import time
from selenium import webdriver
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from time import sleep
from typing import Sequence, AnyStr, NoReturn, Optional


class TradingViewBot:
    def __init__(self, urls: Sequence[AnyStr], comments: Sequence[AnyStr], logs_path: Optional[AnyStr] = None):
        """
        Bot, that goes through every link, provided in "urls" and writes random comments from "comments" under first
        3 posts of every page

        :param urls: List of urls leading to traders' pages
        :param comments: List of comments to be inserted into every comment section
        :param logs_path: Path to file, where the logs are going to be saved. If None, then no logs are saved
        """
        self._urls = urls
        self._comments = comments
        self._driver = webdriver.Chrome()
        self._action = webdriver.ActionChains(self._driver)  # Mouse simulator
        self._check_posts = 3  # How many posts to look through in every page
        self._wait_time = 10  # Seconds to wait for page load. If exceeded, page is skipped

        # If logs_path is not provided (None), creates unusable logger with no output
        if logs_path:
            # Creating a file if it does not exist
            open(logs_path, 'a').close()

            # Setting up logger
            self._logger = logging.getLogger(__name__)
            c_handler = logging.FileHandler(logs_path)
            c_format = logging.Formatter('[%(levelname)s] (%(asctime)s) %(message)s')
            c_handler.setFormatter(c_format)
            self._logger.addHandler(c_handler)
            self._logger.setLevel(logging.INFO)
        else:
            self._logger = logging.getLogger(__name__)
            self._logger.setLevel(logging.CRITICAL)

        self._logger.info('Bot object created')

    def run(self) -> NoReturn:
        """
        Upon calling starts main loop that iterate over every provided URL and tries to place a comment

        :return: None
        """
        for url in tqdm(self._urls):
            self._driver.get(url)
            self._logger.info(f'Processing page: "{url}"')
            self._process_page()

    def _process_page(self) -> NoReturn:
        """
        For every page this method looks for all ideas cards and writes comment under every card, where the flag is not
        marked. Maximum up to self._check_posts will be looked through.

        :return: None
        """
        cards = self._driver.find_elements(
            By.CSS_SELECTOR,
            '#tv-content > div.tv-layout-width > div > div.tv-feed__page.tv-feed__page--no-vindent.published-charts.i-active > div.tv-card-container > div > div > div > div'
        )
        cards = cards[:self._check_posts]
        comment_btns = [card.find_element(By.CSS_SELECTOR,
                                          'div.tv-social-row.tv-widget-idea__social-row > div.tv-social-row__end.tv-social-row__end--adjusted > a')
                        for card in cards]
        flag_btns = [card.find_element(By.CSS_SELECTOR,
                                       'div.tv-social-row.tv-widget-idea__social-row > div.tv-social-row__end.tv-social-row__end--adjusted > span.tv-card-social-item.apply-common-tooltip.tv-card-social-item--favorite.tv-card-social-item--button.tv-card-social-item--rounded.tv-social-row__item.tv-social-row__item--rounded')
                     for card in cards]

        for i in range(self._check_posts):
            self._process_card(comment_btns[i], flag_btns[i])

    def _process_card(self, comment_btn: Sequence[WebElement], flag_btn: Sequence[WebElement]) -> NoReturn:
        """"""
        if 'i-checked' in flag_btn.get_attribute('class'):
            return

        self._action.move_to_element(comment_btn)
        self._action.perform()
        self._action.click(comment_btn)

        comment_section = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.js-textarea'))
        )
        self._action.move_to_element(comment_section)
        self._action.perform()

        comment = random.choice(self._comments)
        comment_section.clear()
        comment_section.send_keys(comment)

        post_comment_btn = self._driver.find_element(By.CSS_SELECTOR, '.tv-button__loader')
        self._action.move_to_element(post_comment_btn)
        self._action.perform()
        self._action.click()

    def stop(self):
        self._driver.quit()
