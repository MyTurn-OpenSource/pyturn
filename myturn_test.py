#!/usr/bin/python3
'''
multiuser test of MyTurn implementations

this one is geared to pyturn
'''
import sys, os, unittest, time, logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)
CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument('--headless')
WEBDRIVER = webdriver.Chrome(chrome_options=CHROME_OPTIONS)

class TestMyturnLoad(unittest.TestCase):
    '''
    Make sure JavaScript runs in headless browser
    '''
    def test_load(self):
        WEBDRIVER.get('http://uwsgi-alpha.myturn.local')
        time.sleep(1)  # enough time for redirect
        logging.debug('current URL: %s', WEBDRIVER.current_url)
        self.assertTrue(WEBDRIVER.current_url.endswith('/app'))

if __name__ == '__main__':
    unittest.main()
