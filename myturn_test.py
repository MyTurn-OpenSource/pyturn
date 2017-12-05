#!/usr/bin/python3
'''
multiuser test of MyTurn implementations

this one is geared to pyturn
'''
import sys, os, unittest, time, logging
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)

class TestMyturnApp(unittest.TestCase):
    '''
    Various tests of app functionality
    '''

    def setUp(self):
        '''
        Initialize test environment
        '''
        capabilities = DesiredCapabilities.PHANTOMJS
        capabilities['loggingPrefs'] = {'browser': 'ALL'}
        self.driver = webdriver.PhantomJS(desired_capabilities=capabilities)

    def test_load(self):
        '''
        Make sure JavaScript runs in headless browser
        '''
        self.driver.get('http://uwsgi-alpha.myturn.local')
        time.sleep(1)  # enough time for redirect
        logging.debug('current URL: %s', self.driver.current_url)
        for entry in (
                self.driver.get_log('browser') + self.driver.get_log('har')):
            logging.debug('browser log entry: %s', entry)
        self.assertTrue(self.driver.current_url.endswith('/app'))

    def tearDown(self):
        '''
        Cleanup after testing complete
        '''
        self.driver.quit()


if __name__ == '__main__':
    '''
    Run all tests
    '''
    unittest.main()
