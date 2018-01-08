#!/usr/bin/python3
'''
multiuser test of MyTurn implementations

this one is geared to pyturn
'''
import sys, os, unittest, time, logging, uuid, tempfile, threading
from datetime import datetime
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidElementStateException
from selenium.common.exceptions import WebDriverException
logging.basicConfig(
    level=logging.DEBUG if __debug__ else logging.INFO,
    format='%(asctime)s:%(levelname)s:%(threadName)s:%(message)s')
QUERY_STRING = '?debug=button&debug=issue1'
WEBPAGE = 'http://uwsgi-alpha.myturn.local/' + QUERY_STRING
EXPECTED_EXCEPTIONS = (
    NoSuchElementException,
    InvalidElementStateException,
)
BROWSER = os.getenv('USE_TEST_BROWSER', 'PhantomJS')
WEBDRIVER = getattr(webdriver, BROWSER)

def find_element(driver, finder, identifier):
    '''
    Convenience routine for finding element
    '''
    element = getattr(driver, 'find_element_by_' + finder)(identifier)
    return element

def currentpath(driver):
    '''
    Return just the pathname part of the URL
    '''
    return urlparse.urlsplit(driver.current_url).path

def savescreen(driver, fileprefix):
    '''
    Save screen to a unique filename for debugging
    '''
    descriptor, filename = tempfile.mkstemp(prefix=fileprefix, suffix='.png')
    logging.warning('Saving screenshot to %s', filename)
    try:  # HTMLUnit doesn't support screenshots
        driver.save_screenshot(filename)
    except WebDriverException:
        # fire up a complete browser to take a shot of the HTML
        source, htmlfile = tempfile.mkstemp(prefix=fileprefix, suffix='.html')
        os.write(source, driver.page_source.encode())
        os.close(source)
        photographer = WEBDRIVER()
        photographer.get(htmlfile)
        photographer.save_screenshot(filename)
        photographer.quit()

def joingroup(driver, username=None, groupname=None):
    '''
    Fill out "join" form. Leave groupname unspecified for default.
    '''
    if username is not None:
        try:
            field = find_element(driver, 'css_selector',
                                 'input[name="username"]')
            field.send_keys(username)
        except EXPECTED_EXCEPTIONS:
            savescreen(driver, 'username_input_')
            raise
    if groupname is not None:
        try:
            field = find_element(driver, 'id', 'group-select')
        except EXPECTED_EXCEPTIONS:
            savescreen(driver, 'groupselect_')
            raise
        Select(field).select_by_value(groupname)
    logging.debug('joingroup field: %s: %s', field, dir(field))
    field = find_element(driver, 'css_selector',
                        'input[name="submit"][value="Join"]')
    field.click()

def newgroup(driver, groupname, minutes, turntime):
    '''
    Fill out group entry form
    '''
    field = find_element(driver, 'css_selector', 'input[name="groupname"]')
    field.send_keys(groupname)
    field = find_element(driver, 'css_selector', 'input[name="total"]')
    field.send_keys(str(minutes))
    field = find_element(driver, 'css_selector', 'input[name="turn"]')
    field.send_keys(str(turntime))
    field = find_element(driver, 'css_selector', 'input[value="Submit"]')
    field.click()

def myturn(driver, release=False):
    '''
    Activate or deactivate `My Turn` button
    '''
    try:
        button = find_element(driver, 'id', 'myturn-button')
    except EXPECTED_EXCEPTIONS:
        savescreen(driver, 'myturnbutton_')
        raise
    actions = ActionChains(driver)
    if release:
        logging.debug('releasing My Turn button')
        actions.release(button)
    else:
        logging.debug('clicking and holding My Turn button')
        actions.click_and_hold(button)
    actions.perform()

def driverlogger(driver):
    '''
    Check constantly for JavaScript logs and output to Python logger
    '''
    index = None  # index into log returned by get_log
    while True:
        messages = driver.get_log('browser')
        logger = logging.getLogger(threading.current_thread().name)
        if len(messages):
            index = index or 0
            while messages[index:]:
                message = messages[index]
                logtime = datetime.fromtimestamp(message['timestamp'] / 1000)
                logger.debug(message['message'].rstrip(' (:)') +
                            (' (%s)' % logtime.isoformat()[11:23]))
                index += 1
        time.sleep(.005)

def active_speaker(driver):
    '''
    return active speaker as shown in upper-left of discussion page
    '''
    status = find_element(driver, 'id', 'talksession-speaker').text
    return status.split()[-1]

class TestMyturnApp(unittest.TestCase):
    '''
    Various tests of basic app functionality
    '''

    def setUp(self):
        '''
        Initialize test environment
        '''
        self.driver = WEBDRIVER()
        self.driver.implicit_wait = 5

    def test_load(self):
        '''
        Make sure JavaScript runs in headless browser
        '''
        logger = threading.Thread(target=driverlogger,
                                        name='console.log',
                                        args=(self.driver,))
        logger.daemon = True  # so main thread doesn't hang at end
        logger.start()
        self.driver.get(WEBPAGE)
        time.sleep(1)  # enough time for redirect
        logging.debug('current URL: %s', self.driver.current_url)
        self.assertEqual(currentpath(self.driver), '/app')

    def test_single(self):
        '''
        Run single-user "conversation" start to finish
        '''
        logger = threading.Thread(target=driverlogger,
                                        name='console.log',
                                        args=(self.driver,))
        logger.daemon = True  # so main thread doesn't hang at end
        logger.start()
        time.sleep(1)  # wait for redirect to /app
        self.driver.get(WEBPAGE)
        joingroup(self.driver, 'tester', '')
        newgroup(self.driver, 'testing', 1, 2)
        joingroup(self.driver, groupname='testing')
        myturn(self.driver)
        time.sleep(10)
        savescreen(self.driver, 'before_releasing_myturn_')
        myturn(self.driver, release=True)
        time.sleep(50.5);
        try:
            report = find_element(self.driver, 'id', 'report-table')
            logging.info('report: %s', report)
        except EXPECTED_EXCEPTIONS:
            savescreen(self.driver, 'report_')
            raise

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
        self.alice = WEBDRIVER()
        self.alice.implicit_wait = 5
        alice_logger = threading.Thread(target=driverlogger,
                                        name='alice',
                                        args=(self.alice,))
        alice_logger.daemon = True  # so main thread doesn't hang at end
        alice_logger.start()
        self.bob = WEBDRIVER()
        self.bob.implicit_wait = 5
        bob_logger = threading.Thread(target=driverlogger,
                                        name='bob',
                                        args=(self.bob,))
        bob_logger.daemon = True  # so main thread doesn't hang at end
        bob_logger.start()
        self.charlie = webdriver.Remote(desired_capabilities=noscript)
        self.charlie.implicit_wait = 5
        # htmlunit doesn't have a logger, javascript is not enabled

    def test_load(self):
        '''
        Make sure JavaScript doesn't run where we want to test /noscript
        '''
        self.charlie.get(WEBPAGE)
        time.sleep(5)  # enough time for refresh
        self.assertEqual(currentpath(self.charlie), '/noscript')

    def test_issue_1(self):
        '''
        Stale display on update

        https://github.com/MyTurn-OpenSource/pyturn/issues/1
        '''
        self.charlie.get(WEBPAGE)
        self.assertEqual(currentpath(self.charlie), '/noscript')
        time.sleep(5)  # time for auto refresh to /noscript page
        self.alice.get(WEBPAGE)
        time.sleep(1)  # get past splash screen
        joingroup(self.alice, 'alice')
        newgroup(self.alice, 'issue1', 1, 10)
        joingroup(self.alice, None, 'issue1')
        # clock should now be ticking on this group
        self.charlie.refresh()  # Charlie won't see new group until he refreshes
        joingroup(self.charlie, 'charlie', 'issue1')
        logging.debug('issue1: charlie pressing My Turn button')
        find_element(self.charlie, 'id', 'myturn-button').click()
        find_element(self.charlie, 'id', 'check-status').click()
        status = find_element(self.charlie, 'id', 'talksession-speaker').text
        self.assertEqual(active_speaker(self.charlie), 'charlie')
        logging.debug('issue1: alice pressing My Turn button')
        myturn(self.alice)
        logging.debug('issue1: waiting until alice is active speaker')
        while active_speaker(self.alice) != 'alice':
            time.sleep(.1)
        find_element(self.charlie, 'id', 'check-status').click()
        # the following fails when server under heavy load, see issue #1
        logging.debug('issue1: checking charlie sees alice as active speaker')
        self.assertEqual(active_speaker(self.charlie), 'alice')

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

if __name__ == '__main__':
    '''
    Run all tests
    '''
    unittest.main()
