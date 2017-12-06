#!/usr/bin/python3
'''
multiuser test of MyTurn implementations

this one is geared to pyturn
'''
import sys, os, unittest, time, logging
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)

class TestMyturnApp(unittest.TestCase):
    '''
    Various tests of basic app functionality
    '''

    def setUp(self):
        '''
        Initialize test environment
        '''
        self.driver = webdriver.PhantomJS()

    def test_load(self):
        '''
        Make sure JavaScript runs in headless browser
        '''
        self.driver.get('http://uwsgi-alpha.myturn.local')
        time.sleep(1)  # enough time for redirect
        logging.debug('current URL: %s', self.driver.current_url)
        for entry in self.driver.get_log('browser'):
            logging.debug('browser log entry: %s', entry)
        self.assertTrue(self.driver.current_url.endswith('/app'))

    def tearDown(self):
        '''
        Cleanup after testing complete
        '''
        self.driver.quit()

class TestMyturnMultiUser(unittest.TestCase):
    '''
    Various tests of interaction between app and multiple users
    '''

    def setUp(self):
        '''
        Initialize test environment
        '''
        noscript = DesiredCapabilities.HTMLUNIT
        noscript['javascriptEnabled'] = False
        self.alice = webdriver.PhantomJS()
        self.bob = webdriver.PhantomJS()
        self.charlie = webdriver.Remote(desired_capabilities=noscript)

    def test_load(self):
        '''
        Make sure JavaScript doesn't run where we want to test /noscript
        '''
        self.charlie.get('http://uwsgi-alpha.myturn.local')
        time.sleep(5)  # enough time for refresh
        self.assertEqual(self.charlie.current_url.split('/')[-1], 'noscript')

    def tearDown(self):
        '''
        Cleanup after testing complete
        '''
        self.alice.quit()
        self.bob.quit()
        self.charlie.quit()

class TestMyturnStress(unittest.TestCase):
    '''
    Stress-test server
    '''

    def setUp(self):
        '''
        Initialize test environment
        '''
        self.driver = webdriver.PhantomJS()

    def test_load(self):
        '''
        Make sure JavaScript runs in headless browser
        '''
        self.driver.get('http://uwsgi-alpha.myturn.local')
        time.sleep(1)  # enough time for redirect
        logging.debug('current URL: %s', self.driver.current_url)
        for entry in self.driver.get_log('browser'):
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
