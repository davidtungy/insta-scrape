from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from scrape_paths import *

def is_xpath_present(browser, xpath):
	return len(browser.find_elements_by_xpath(xpath)) > 0

def get_instagram_url(selector):
	s = '/' + selector + '/'
	return INSTAGRAM_TEMPLATE.format(s.replace("//", "/"))

def get_element_count(browser, path):
	attribute = browser.find_element_by_xpath(path).get_attribute('innerHTML')
	return int(attribute.replace(',', '').strip())
