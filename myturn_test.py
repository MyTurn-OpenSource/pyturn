#!/usr/bin/python3
'''
multiuser test of MyTurn implementations

this one is geared to pyturn
'''
import sys, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument('--headless')
WEBDRIVER = webdriver.Chrome()
