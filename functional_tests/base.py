import os
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

MAX_WAIT = 10


class FunctionalTest(StaticLiveServerTestCase):

    @classmethod
    def setUp(self):
        super().setUpClass()
        self.browser = webdriver.Chrome()
    
    @classmethod
    def tearDownClass(self):
        self.browser.quit()
        super().tearDownClass()

    def wait_for(self, fn):
        start_time = time.time()
        while True:
            try:
                return fn()
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)
