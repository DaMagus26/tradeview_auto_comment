import logging
import random
import numpy as np
import time
import re
from selenium import webdriver
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from time import sleep
from typing import Sequence, AnyStr, NoReturn, Optional, Literal


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
        self._sleep = True  # If False, then any time.sleep() using this parameter will not work. Hence, faster execution

        # FIXME
        self._username = 'Akaguma7'
        self._password = 'uNAkB5cD'

        # Retrieving domain name from the first link to be able to log in
        url = re.compile(r'^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+)')
        self._main_page = url.match(urls[0])[0]

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
        # self._login()
        self._manual_login()

    def spell_into_input(self, input_area, text, interval, rand=True):
        input_area.clear()
        for key in text:
            input_area.send_keys(key)
            sleep(int(self._sleep) and max(np.random.normal(interval, interval * 0.9), 0.01))

    def _login(self) -> Literal[True, False]:
        """
        If not already, tries to log in to the website.

        :return: Returns True if was already logged in, False otherwise
        """
        self._driver.get(self._main_page)
        account_btns = self._driver.find_elements(By.CSS_SELECTOR, 'body > div.tv-main > div.tv-header.tv-header__top.js-site-header-container.tv-header--sticky > div.tv-header__inner > div.tv-header__area.tv-header__area--user > button.tv-header__user-menu-button.js-header-user-menu-button')
        # children = [element.tag_name for element in account_btn.find_elements(By.CSS_SELECTOR, '*')]
        if 'logged' in account_btns[0].get_attribute('class'):
            if account_btns[0].is_displayed():
                self._logger.info('Logged button is displayed. Already logged in. Starting processing URLs.')
                return True
            else:
                btn = account_btns[1]
        else:
            if account_btns[1].is_displayed():
                self._logger.info('Logged button is displayed. Already logged in. Starting processing URLs.')
                return True
            else:
                btn = account_btns[0]

        self._logger.info('Need to log in first')
        self._action.move_to_element(btn)
        self._action.perform()
        btn.click()
        sleep(int(self._sleep) and 0.5)

        # Attempt to get to authorization screen step by step
        sign_in_btn = WebDriverWait(self._driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span.label-mDJVFqQ3.label-jFqVJoPk.label-mDJVFqQ3.label-YQGjel_5.js-main-menu-dropdown-link-title'))
        )
        self._action.move_to_element(sign_in_btn)
        self._action.perform()
        sign_in_btn.click()

        email_btn = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'Email'))
        )
        sleep(int(self._sleep) and 1)
        self._action.move_to_element(email_btn)
        self._action.perform()
        sleep(int(self._sleep) and 0.2)
        email_btn.click()

        email_input = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.ID, 'id_username'))
        )
        sleep(int(self._sleep) and 2)
        self._action.move_to_element(email_input)
        self._action.perform()
        email_input.click()
        sleep(int(self._sleep) and 0.5)
        self.spell_into_input(email_input, self._username, 0.05)

        password_input = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.ID, 'id_password'))
        )
        sleep(int(self._sleep) and 0.5)
        self._action.move_to_element(password_input)
        self._action.perform()
        password_input.click()
        sleep(int(self._sleep) and 0.5)
        self.spell_into_input(password_input, self._password, 0.05)

        sleep(int(self._sleep) and 0.5)
        remember_me = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.wrapper-GZajBGIm'))
        )
        self._action.move_to_element(remember_me)
        self._action.perform()
        remember_me.click()

        sleep(int(self._sleep) and 1.5)
        submit_btn = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.submitButton-LQwxK8Bm'))
        )
        self._action.move_to_element(submit_btn)
        self._action.perform()
        sleep(int(self._sleep) and 0.2)
        submit_btn.click()

        return False

    def _manual_login(self) -> NoReturn:
        self._driver.get(self._main_page)
        old_sleep = self._sleep
        self._sleep = 0
        account_btns = self._driver.find_elements(By.CSS_SELECTOR,
                                                  'body > div.tv-main > div.tv-header.tv-header__top.js-site-header-container.tv-header--sticky > div.tv-header__inner > div.tv-header__area.tv-header__area--user > button.tv-header__user-menu-button.js-header-user-menu-button')
        # children = [element.tag_name for element in account_btn.find_elements(By.CSS_SELECTOR, '*')]
        if 'logged' in account_btns[0].get_attribute('class'):
            if account_btns[0].is_displayed():
                self._logger.info('Logged button is displayed. Already logged in. Starting processing URLs.')
                return True
            else:
                btn = account_btns[1]
        else:
            if account_btns[1].is_displayed():
                self._logger.info('Logged button is displayed. Already logged in. Starting processing URLs.')
                return True
            else:
                btn = account_btns[0]

        self._logger.info('Need to log in first')
        self._action.move_to_element(btn)
        self._action.perform()
        btn.click()
        sleep(int(self._sleep) and 0.5)

        # Attempt to get to authorization screen step by step
        sign_in_btn = WebDriverWait(self._driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            'span.label-mDJVFqQ3.label-jFqVJoPk.label-mDJVFqQ3.label-YQGjel_5.js-main-menu-dropdown-link-title'))
        )
        self._action.move_to_element(sign_in_btn)
        self._action.perform()
        sign_in_btn.click()

        email_btn = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'Email'))
        )
        sleep(int(self._sleep) and 1)
        self._action.move_to_element(email_btn)
        self._action.perform()
        sleep(int(self._sleep) and 0.2)
        email_btn.click()

        email_input = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.ID, 'id_username'))
        )
        sleep(int(self._sleep) and 2)
        self._action.move_to_element(email_input)
        self._action.perform()
        email_input.click()
        sleep(int(self._sleep) and 0.5)
        self.spell_into_input(email_input, self._username, 0.05)

        password_input = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.ID, 'id_password'))
        )
        sleep(int(self._sleep) and 0.5)
        self._action.move_to_element(password_input)
        self._action.perform()
        password_input.click()
        sleep(int(self._sleep) and 0.5)
        self.spell_into_input(password_input, self._password, 0.05)

        sleep(int(self._sleep) and 0.5)
        remember_me = WebDriverWait(self._driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.wrapper-GZajBGIm'))
        )
        self._action.move_to_element(remember_me)
        self._action.perform()
        remember_me.click()
        self._sleep = old_sleep

        sleep(45)

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
        # Waits for the pop up window to load
        cards = WebDriverWait(self._driver, self._wait_time).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                 '#tv-content div.tv-card-container > div > div > div > div'))
        )

        cards = cards[:self._check_posts]
        comment_btns = [WebDriverWait(card, self._wait_time).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//div[5]/div[2]/a')))
            for card in cards]
        flag_btns = [WebDriverWait(card, self._wait_time).until(
            EC.presence_of_element_located((By.XPATH,
                                            '//div[5]/div[2]/span[2]')))
            for card in cards]

        print(self._driver.title)
        print('Cards:', len(cards))
        print('btns:', len(flag_btns))
        for i in range(self._check_posts):
            sleep(int(self._sleep) and 2)
            self._process_card(comment_btns[i], flag_btns[i])

    def _process_card(self, comment_btn: WebElement, flag_btn: WebElement) -> NoReturn:
        """
        For every found card this method looks for comment and flag buttons. If flag is marked, then the card is
        skipped. Otherwise, it clicks comments button, waits for it to load and writes a comment in a pop up window

        :param comment_btn: comment button element
        :param flag_btn: flag button element
        :return: None
        """
        if 'i-checked' in flag_btn.get_attribute('class'):
            print('Clicked')
            return

        self._action.move_to_element(comment_btn)
        self._action.perform()
        sleep(int(self._sleep) and 0.5)
        comment_btn.click()

        # Waits for the pop up window to load
        comment_section = WebDriverWait(self._driver, self._wait_time).until(
            EC.presence_of_element_located((By.NAME, 'comment'))
        )
        self._action.move_to_element(comment_section)
        self._action.perform()
        sleep(int(self._sleep) and 1)
        comment_section.click()

        # Picks and inserts a random comment
        comment = random.choice(self._comments)
        self.spell_into_input(comment_section, comment, 0.08)

        # JS_ADD_TEXT_TO_INPUT = """
        #   var elm = arguments[0], txt = arguments[1];
        #   elm.value += txt;
        #   elm.dispatchEvent(new Event('change'));
        #   """
        # self._driver.execute_script(JS_ADD_TEXT_TO_INPUT, comment_section, comment)

        sleep(int(self._sleep) and 1)
        post_comment_btn = self._driver.find_element(By.CSS_SELECTOR, '#chart-view-comment-form > div.form-container-oUJZRkMk > form > div > button.button-R4AggD4r.button-D4RPB3ZC.size-small-D4RPB3ZC.color-brand-D4RPB3ZC.variant-primary-D4RPB3ZC')
        self._action.move_to_element(post_comment_btn)
        self._action.perform()
        sleep(int(self._sleep) and 0.3)
        post_comment_btn.click()

        close_btn = WebDriverWait(self._driver, self._wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#overlap-manager-root > div > div.tv-dialog__modal-wrap > div > div > div > div.tv-chart-view__dialog-close.tv-dialog__close.tv-dialog__close--new-style.js-dialog__close > svg'))
        )

        sleep(int(self._sleep) and 0.5)
        self._action.move_to_element(close_btn)
        self._action.perform()
        sleep(int(self._sleep) and 0.3)
        close_btn.click()

        sleep(int(self._sleep) and 1)
        flag_btn.click()

    def stop(self):
        self._driver.quit()
