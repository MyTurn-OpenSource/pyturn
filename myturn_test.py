#!/usr/bin/python3
'''
multiuser test of MyTurn implementations

this one is geared to pyturn
'''
import sys, os, unittest, time, logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)
WEBPAGE = 'http://uwsgi-alpha.myturn.local/'

def joingroup(driver, username, groupname=None):
    '''
    Fill out "join" form. Leave groupname unspecified for default.
    '''
    field = driver.find_element_by_css_selector('input[name="username"]')
    field.send_keys(username)
    if groupname is not None:
        try:
            field = driver.find_element_by_id('group-select')
        except NoSuchElementException:
            driver.save_screenshot('/tmp/errorscreen.png')
            logging.error('see /tmp/errorscreen.png for error')
            raise
        Select(field).select_by_value(groupname)
    logging.debug('joingroup field: %s: %s', field, dir(field))
    field = driver.find_element_by_css_selector(
        'input[name="submit"][value="Join"]')
    field.click()

def newgroup(driver, groupname, minutes, turntime):
    '''
    Fill out group entry form
    '''
    field = driver.find_element_by_css_selector('input[name="groupname"]')
    field.send_keys(groupname)
    field = driver.find_element_by_css_selector('input[name="total"]')
    field.send_keys(str(minutes))
    field = driver.find_element_by_css_selector('input[name="turn"]')
    field.send_keys(str(turntime))
    field = driver.find_element_by_css_selector('input[value="Submit"]')
    field.click()

def myturn(driver, release=False):
    '''
    Activate or deactivate `My Turn` button
    '''
    button = driver.find_element_by_id('myturn-button')
    actions = ActionChains(driver)
    if release:
        actions.release(button)
    else:
        actions.click_and_hold(button)
    actions.perform()

class TestMyturnApp(unittest.TestCase):
    '''
    Various tests of basic app functionality
    '''

    def setUp(self):
        '''
        Initialize test environment
        '''
        self.driver = webdriver.PhantomJS()
        self.driver.implicit_wait = 5

    def test_load(self):
        '''
        Make sure JavaScript runs in headless browser
        '''
        self.driver.get(WEBPAGE)
        time.sleep(1)  # enough time for redirect
        logging.debug('current URL: %s', self.driver.current_url)
        for entry in self.driver.get_log('browser'):
            logging.debug('browser log entry: %s', entry)
        self.assertTrue(self.driver.current_url.endswith('/app'))

    def test_single(self):
        '''
        Run single-user "conversation" start to finish
        '''
        time.sleep(1)  # wait for redirect to /app
        self.driver.get(WEBPAGE)
        joingroup(self.driver, 'tester', '')
        newgroup(self.driver, 'testing', 1, 2)
        joingroup(self.driver, 'tester', 'testing')
        myturn(self.driver)
        time.sleep(10)
        myturn(self.driver, release=True)
        time.sleep(50.5);
        report = self.driver.find_element_by_id('report-table')
        logging.debug('report: %s', report)

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
        self.alice.implicit_wait = 5
        self.bob = webdriver.PhantomJS()
        self.bob.implicit_wait = 5
        self.charlie = webdriver.Remote(desired_capabilities=noscript)
        self.charlie.implicit_wait = 5

    def test_load(self):
        '''
        Make sure JavaScript doesn't run where we want to test /noscript
        '''
        self.charlie.get(WEBPAGE)
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
        self.driver.implicit_wait = 5

    def test_load(self):
        '''
        Make sure JavaScript runs in headless browser
        '''
        self.driver.get(WEBPAGE)
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
