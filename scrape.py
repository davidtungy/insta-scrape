import argparse
import contextlib
import os
import pickle
import sys
import time

from scrape_utils import *
from scrape_paths import *

from os import path
from random import randint

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd

DIR_PATH = ''

# TO DO:
# (1) Refactor a bunch of these constants/repetitive code into functions
#     within a utility class
# (2) Add functionality to update cache (pick up only new post information)
#     Needs to handle updating likes/info of recent posts that may have been
#     iteracted with
# (3) If username or password is not set (different than incorrect), continue
#     execution instead of early stopping (IG sets a redirect when attempting
#     to switch browsers)
# (4) Create main.py, which should be the driver that calls scrape.py 
#     (this) and analysis.py for DataFrame textual analysis
# (5) If needed, can add additional scraped material (probably not pictures
#     due to privacy) to cleaned_posts, e.g. IG tagging the post as a 
#     screenshot of Twitter, photo text that is pre-provided

def main(args):
	# Create directory to write to
	os.makedirs(args.username, exist_ok=True)
	DIR_PATH = args.username
	POST_CACHE = os.path.join(DIR_PATH, 'posts.txt')
	CSV_CACHE = os.path.join(DIR_PATH, 'data.csv')

	options = webdriver.ChromeOptions()
	options.add_argument('--ignore-certificate-errors')
	#options.add_argument('--incognito')
	#options.add_argument('--headless')
	browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)

	authenticate(browser, args.user, args.password, use_cache=True)
	#authenticate(browser, args.user, args.password, use_cache=False)

	# If log-in failed, this code will execute as well
	if not is_valid_username(browser, args.username):
		print("User", args.username, "could not be accessed.")
		browser.quit()
		return

	followers, following = get_follow_counts(browser, args.username)

	print("My boy has", followers, "followers and is following", following)
	print("Follow ratio of ", followers/following)

	if is_private(browser, args.username):
		print("Instagram is private. Must log-in and be a follower to see posts.")
		browser.quit()
		return

	urls = get_post_urls(browser, max_posts=800, use_cache=True, cache_location=POST_CACHE)
	#urls = getPostUrls(browser, max_posts=500, use_cache=False)
	with open(POST_CACHE, "w") as f:
		f.seek(0)
		f.truncate()
		f.write("\n".join(urls))
	print("---")
	print(len(urls), " posts to scrutinize...")

	cleaned_posts = clean_posts(browser, urls)

	browser.quit()

	# Save to dataframe for analysis
	df = pd.DataFrame(cleaned_posts)
	df.to_csv(CSV_CACHE, encoding='utf-8', index=True)

	print("Completed.")

def authenticate(browser, username, password, use_cache=False, save_cookie=True):
	browser.get(LOGIN_URL)
	if use_cache and path.exists(COOKIE_PATH):
		# Set browser cookie information to log-in
		print("Authenticating via cookie set in: ", COOKIE_PATH, "...")
		# Must be in the same domain to apply cookies
		with open(COOKIE_PATH, 'rb') as cookiesfile:
			cookies = pickle.load(cookiesfile)
			for cookie in cookies:
				browser.add_cookie(cookie)
	elif username is not None and password is not None:
		# Log in with given user information
		print("Logging in with given username and password...")
		time.sleep(1)
		browser.find_element_by_xpath(LOGIN_FIELD_USERNAME).send_keys(username)
		browser.find_element_by_xpath(LOGIN_FIELD_PASSWORD).send_keys(password)
		time.sleep(1)
		try:
			browser.find_element_by_xpath(LOGIN_FIELD_SUBMIT).click()
		except ElementClickInterceptedException:
			print("Could not log-in. Username and/or password may have been entered incorrectly, scraping may not be able to work as intended.")
			return

		time.sleep(5)
		if is_xpath_present(browser, LOGIN_INCORRECT):
			print("Username and/or password entered incorrectly, scraping may not be able to work as intended.")
			return
		browser.find_element_by_xpath(LOGIN_LOGIN_SAVE).click()
		time.sleep(5)
		# Looks like HTML changes dynamically (possibly day by day to prevent bots)
		if is_xpath_present(browser, LOGIN_NOTIFICATIONS_1):
			browser.find_element_by_xpath(LOGIN_NOTIFICATIONS_1).click()
		elif is_xpath_present(browser, LOGIN_NOTIFICATIONS_2):
			browser.find_element_by_xpath(LOGIN_NOTIFICATIONS_2).click()
		else:
			browser.find_element_by_xpath(LOGIN_NOTIFICATIONS_3).click()
		time.sleep(1)
		# Save cookie
		if save_cookie:
			print("Saving cookie...")
			with open(os.path.join(os.path.dirname(__file__), COOKIE_PATH), 'wb') as filehandler:
				pickle.dump(browser.get_cookies(), filehandler)
	else:
		print("No username and/or password given, scraping may not be able to work as intended.")

def is_valid_username(browser, user):
	browser.get(get_instagram_url(user))
	time.sleep(5)
	return not is_xpath_present(browser, INVALID_USER)

def get_follow_counts(browser, user):
	browser.get(get_instagram_url(user))
	time.sleep(5)
	followers = get_element_count(browser, FOLLOWERS_COUNT)
	following = get_element_count(browser, FOLLOWING_COUNT)
	return followers, following

def is_private(browser, user):
	browser.get(get_instagram_url(user))
	time.sleep(5)
	return is_xpath_present(browser, PRIVATE_PROFILE)
	
# Scroll to bottom of the browser to pick up dynamically-loaded content
# Assumes that there isn't an exponential increase in render time
# A maximum of 32 posts or so can be displayed at a time
# Added a max post count (if someone has a crazy amount of posts)
# Returns individual post urls in chronological order (oldest first)
def get_post_urls(browser, max_posts=100, timeout=2, use_cache=False, cache_location='posts.txt'):
	if use_cache:
		if path.exists(cache_location):
			with open(cache_location) as f:
				return f.read().splitlines()
		else:
			print("Could not find cache at location:", cache_location)
	urls = []
	prev = browser.execute_script(JS_GET_SCROLL_HEIGHT)
	while True:
		print("Scrolling")
		browser.execute_script(JS_SCROLL_TO_BOTTOM)
		time.sleep(timeout)
		curr = browser.execute_script(JS_GET_SCROLL_HEIGHT)
		element = browser.find_element_by_xpath(BODY).get_attribute('outerHTML')
		soup = BeautifulSoup(element, 'html.parser')
		posts = soup.select(POST_DIV)
		for p in posts:
			link = p.find('a')['href']
			if link not in urls:
				urls.append(link)
			if len(urls) == max_posts:
				return urls
		if curr == prev:
			print("Retry")
			time.sleep(timeout + 2)
			curr = browser.execute_script(JS_GET_SCROLL_HEIGHT)
			if curr == prev:
				break
			timeout += 2
		prev = curr
	urls.reverse()
	return urls

# Returns a list of dictionary items with the following fields:
#	- caption:		Instagram caption
#	- post_type:	'image' or 'video'
#	- views:		Number of views of video post
#	- likes:		Number of likes on the post
#	- date:			Date of post (e.g. Jul 30, 2021)
# List objects are in the same order as their URL was received
def clean_posts(browser, urls):
	cleaned_posts = []

	for url in urls:
		browser.get(get_instagram_url(url))
		soup = BeautifulSoup(browser.page_source, 'html.parser')

		# Wait until page render
		# Sometimes may have to trigger a refresh (may be an Instagram rendering issue)
		while not is_xpath_present(browser, CAPTION):
			time.sleep(1)
			soup = BeautifulSoup(browser.page_source, 'html.parser')

		caption = browser.find_element_by_xpath(CAPTION).get_attribute('innerHTML')
		
		# Handle images
		if soup.find('video') is None:
			post_type = 'image'
			views = None
			if is_xpath_present(browser, IMAGE_LIKED_BY_X):
				# Liked by X and <> others
				likes = 1
				if is_xpath_present(browser, IMAGE_LIKED_BY_X_AND_OTHERS):
					likes += int(browser.find_element_by_xpath(IMAGE_LIKED_BY_X_AND_OTHERS).get_attribute('innerHTML'))
			elif is_xpath_present(browser, IMAGE_ONE_LIKE):
				# 1 like
				likes = 1
			else:
				# Liked by <> others
				likes = int(browser.find_element_by_xpath(IMAGE_LIKED_BY_OTHERS).get_attribute('innerHTML'))
			date = browser.find_element_by_xpath(IMAGE_DATE).get_attribute('title')
		# Handle videos
		else:
			post_type = 'video'
			if is_xpath_present(browser, VIDEO_VIEWS):
				views_element = browser.find_element_by_xpath(VIDEO_VIEWS)
				views = int(views_element.get_attribute('innerHTML'))
				views_element.click()
				likes = int(browser.find_element_by_xpath(VIDEO_LIKES).get_attribute('innerHTML'))
				date = browser.find_element_by_xpath(VIDEO_DATE).get_attribute('title')
			# Some videos are inconsistent and do not display views (structured as images, possibly uploaded as gifs?)
			else:
				# No view information for posts of this type
				views = None
				if is_xpath_present(browser, IMAGE_LIKED_BY_X):
					# Liked by X and <> others
					likes = 1
					if is_xpath_present(browser, IMAGE_LIKED_BY_X_AND_OTHERS):
						likes += int(browser.find_element_by_xpath(IMAGE_LIKED_BY_X_AND_OTHERS).get_attribute('innerHTML'))
				elif is_xpath_present(browser, IMAGE_ONE_LIKE):
					# 1 like
					likes = 1
				else:
					# Liked by <> others
					likes = int(browser.find_element_by_xpath(IMAGE_LIKED_BY_OTHERS).get_attribute('innerHTML'))
				date = browser.find_element_by_xpath(IMAGE_DATE).get_attribute('title')
		
		cleaned = {"post_type": post_type, "caption": caption, "likes": likes, "views": views, "date": date}
		cleaned_posts.append(cleaned)
		print("---")
		print(cleaned)
		# Be forgiving to their servers and sleep a short while
		time.sleep(randint(0,3))

	return cleaned_posts

'''
Pretty much need to supply user and password (Instagram doesn't allow non-authenticated viewing boo)
Without authentication, you can only view 15 or so posts from public accounts
'''
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("username", help="Instagram username to process.")
	parser.add_argument("-u", "--user", help="Your Instagram user login. Used to scrape private accounts (must be a follower).")
	parser.add_argument("-p", "--password", help="Your Instagram user password. Used to scrape private accounts (must be a follower).")

	args = parser.parse_args()
	print(args)
	main(args)
