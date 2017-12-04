#!/usr/bin/python3
'''
multiuser test of MyTurn implementations

this one is geared to pyturn
'''
import sys, os, unittest, time, logging
from selenium import webdriver
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)

class TestMyturnApp(unittest.TestCase):
    '''
    Various tests of app functionality
    '''

    def setUp(self):
        '''
        Initialize test environment
        '''
        self.driver = webdriver.Remote(
            desired_capabilities=webdriver.DesiredCapabilities.HTMLUNITWITHJS)

    def test_load(self):
        '''
        Make sure JavaScript runs in headless browser
        '''
        self.driver.get('http://uwsgi-alpha.myturn.local')
        time.sleep(1)  # enough time for redirect
        logging.debug('current URL: %s', self.driver.current_url)
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
