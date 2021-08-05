import argparse
import os
import pickle
import time

from os import path
from random import randint

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

COOKIE_PATH = 'cookie.pkl'
POST_CACHE = 'posts.txt'

# TO DO:
# (1) Refactor a bunch of these constants/repetitive code into functions
#     within a utility class
# (2) Add functionality to update cache (pick up only new post information)
#     Needs to handle updating likes/info of recent posts that may have been
#     iteracted with
# (3) If username or password is not set (different than incorrect), continue
#     execution instead of early stopping (IG sets a redirect when attempting
#     to switch browsers)
# (4) Create main.py, which should be the driver that calls insta_scrape.py 
#     (this) and analysis.py for DataFrame textual analysis
# (5) If needed, can add additional scraped material (probably not pictures
#     due to privacy) to cleaned_posts, e.g. IG tagging the post as a 
#     screenshot of Twitter, photo text that is pre-provided

def main(args):
	options = webdriver.ChromeOptions()
	options.add_argument('--ignore-certificate-errors')
	#options.add_argument('--incognito')
	#options.add_argument('--headless')
	browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
	time.sleep(1)
	soup = BeautifulSoup(browser.page_source, 'lxml')

	#authenticate(browser, args.user, args.password, use_cache=True)
	authenticate(browser, args.user, args.password, use_cache=False)

	# If log-in failed, this code will execute as well
	if isNotValidUsername(browser, args.username):
		print("User", args.username, "could not be accessed.")
		browser.quit()
		return

	followers, following = getFollowCounts(browser, args.username)

	print("My boy has", followers, "followers and is following", following)
	print("Follow ratio of ", followers/following)


	if isPrivate(browser, args.username):
		print("Instagram is private. Must log-in and be a follower to see posts.")
		browser.quit()
		return

	#urls = getPostUrls(browser, max_posts=500, use_cache=True)
	urls = getPostUrls(browser, max_posts=500, use_cache=False)
	print("---")
	print(len(urls), " posts to scrutinize...")

	cleaned_posts = []

	for url in urls:
		post_url = 'https://www.instagram.com{}?hl=en'.format(url)
		browser.get(post_url)
		soup = BeautifulSoup(browser.page_source, 'html.parser')

		# Possibly need to refactor this into a class (or maybe dataframe?)
		caption = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span').get_attribute('innerHTML')
		if soup.find('video') is None:
			post_type = 'image'
			views = None
										
			if isXPATHPresent(browser, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/span/a'):
				# Liked by X and <> others
				likes = 1
				if isXPATHPresent(browser, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/a/span'):
					likes += int(browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/a/span').get_attribute('innerHTML'))
			elif isXPATHPresent(browser, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div/a'):
				# 1 like
				likes = 1
			else:
				# Liked by <> others
				likes = int(browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div/a/span').get_attribute('innerHTML'))
			date = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/div/div/time').get_attribute('title')
		else:
			post_type = 'video'
			if isXPATHPresent(browser, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/span/span'):
				views_element = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/span/span')
				views = int(views_element.get_attribute('innerHTML'))
				views_element.click()
				likes = int(browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div/div[4]/span').get_attribute('innerHTML'))
				date = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[2]/a/time').get_attribute('title')
			else:
				# Some videos are inconsistent and do not display views (appear as images)
				views = None
				caption = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span').get_attribute('innerHTML')

				if isXPATHPresent(browser, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/span/a'):
					likes = 1
					if isXPATHPresent(browser, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/a/span'):
						likes += int(browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/a/span').get_attribute('innerHTML'))
				else:
					likes = int(browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div/a/span').get_attribute('innerHTML'))
				date = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/div/div/time').get_attribute('title')
		
		cleaned = {"post_type": post_type, "caption": caption, "likes": likes, "views": views, "date": date}
		print('----------')
		print(cleaned)
		cleaned_posts.append(cleaned)

		# Be generous to their servers and sleep a short while
		time.sleep(randint(0,3))

	browser.quit()

	# Save to dataframe for analysis
	df = pd.DataFrame(cleaned_posts)
	df.to_csv(args.username + ".csv", encoding='utf-8', index=True)

	print("Creating graph...")
	likes = []
	for post in cleaned_posts:
		likes.append(post["likes"])
	x = np.arange(len(cleaned_posts))
	plt.plot(x, likes, label="Likes")
	plt.title("@" + args.username)
	plt.xlabel("Post")
	plt.ylabel("Likes")
	plt.savefig(args.username + ".png")

	print("Completed.")


def authenticate(browser, username, password, use_cache=False, save_cookie=True):
	page_url = 'https://www.instagram.com/accounts/login/?hl=en'
	browser.get(page_url)
	
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
		browser.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input').send_keys(username)
		browser.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input').send_keys(password)
		time.sleep(1)
		try:
			browser.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[3]/button').click()
		except ElementClickInterceptedException:
			print("Could not log-in. Username and/or password may have been entered incorrectly, scraping may not be able to work as intended.")
			return

		time.sleep(5)
		if isXPATHPresent(browser, '//*[@id="slfErrorAlert"]'):
			print("Username and/or password entered incorrectly, scraping may not be able to work as intended.")
			return
		browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div/div/div/button').click()
		time.sleep(5)
		# Looks like HTML changes dynamically (possibly day by day to prevent bots)
		if isXPATHPresent(browser, '/html/body/div[4]/div/div/div/div[3]/button[2]'):
			browser.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div[3]/button[2]').click()
		elif isXPATHPresent(browser, '/html/body/div[5]/div/div/div/div[3]/button[2]'):
			browser.find_element(By.XPATH, '/html/body/div[5]/div/div/div/div[3]/button[2]').click()
		else:
			browser.find_element(By.XPATH, '/html/body/div[6]/div/div/div/div[3]/button[2]').click()
		time.sleep(1)
		# Save cookie
		if save_cookie:
			print("Saving cookie...")
			with open(os.path.join(os.path.dirname(__file__), COOKIE_PATH), 'wb') as filehandler:
				pickle.dump(browser.get_cookies(), filehandler)
	else:
		print("No username and/or password given, scraping may not be able to work as intended.")

def isXPATHPresent(browser, xpath):
	return len(browser.find_elements(By.XPATH, xpath)) > 0

def isNotValidUsername(browser, user):
	page_url = 'https://www.instagram.com/{}/?hl=en'.format(user)
	browser.get(page_url)
	time.sleep(5)
	return isXPATHPresent(browser, '//*[@id="react-root"]/section/main/div/div/div/div/a')

def getFollowCounts(browser, user):
	page_url = 'https://www.instagram.com/{}/?hl=en'.format(user)
	browser.get(page_url)
	time.sleep(5)
	followers = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span').get_attribute('innerHTML')
	followers = int(followers.replace(',', '').strip())
	following = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/span').get_attribute('innerHTML')
	following = int(following.replace(',', '').strip())
	return followers, following

def isPrivate(browser, user):
	page_url = 'https://www.instagram.com/{}/?hl=en'.format(user)
	browser.get(page_url)
	time.sleep(5)
	return isXPATHPresent(browser, '//*[@id="react-root"]/section/main/div/div/article/div/div/h2')
	
# Scroll to bottom of the browser to pick up dynamically-loaded content
# Assumes that there isn't an exponential increase in render time
# A maximum of 32 posts or so can be displayed at a time
# Added a max post count (if someone has a crazy amount of posts)
# Returns individual post urls in chronological order (oldest first)
def getPostUrls(browser, max_posts=100, timeout=2, use_cache=False):
	if use_cache:
		if path.exists(POST_CACHE):
			with open(POST_CACHE) as f:
				return f.read().splitlines()
	urls = []
	prev = browser.execute_script("return document.body.scrollHeight")
	while True:
		browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(timeout)
		curr = browser.execute_script("return document.body.scrollHeight")
		element = browser.find_element_by_xpath("//body").get_attribute('outerHTML')
		soup = BeautifulSoup(element, 'html.parser')
		posts = soup.select('div.v1Nh3.kIKUG._bz0w')
		for p in posts:
			link = p.find('a')['href']
			if link not in urls:
				urls.append(link)
			if len(urls) == max_posts:
				return urls
		if curr == prev:
			time.sleep(timeout+2)
			if curr == prev:
				break
			timeout += 2
		prev = curr
	urls.reverse()
	with open(POST_CACHE, "w") as f:
		f.seek(0)
		f.truncate()
		f.write("\n".join(urls))
	return urls

# Returns a list of dictionary items with the following fields:
#	- caption:		Instagram caption
#	- post_type:	'image' or 'video'
#	- views:		Number of views of video post
#	- likes:		Number of likes on the post
#	- date:			Date of post (e.g. Jul 30, 2021)
# List objects are in the same order as their URL was received
def cleanPosts(browser, urls):
	cleaned_posts = []

	for url in urls:
		post_url = 'https://www.instagram.com{}?hl=en'.format(url)
		browser.get(post_url)
		soup = BeautifulSoup(browser.page_source, 'html.parser')

		caption = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span').get_attribute('innerHTML')
		
		# Handle images
		if soup.find('video') is None:
			post_type = 'image'
			views = None
			if isXPATHPresent(browser, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/span/a'):
				# Liked by X and <> others
				likes = 1
				if isXPATHPresent(browser, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/a/span'):
					likes += int(browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/a/span').get_attribute('innerHTML'))
			elif isXPATHPresent(browser, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div/a'):
				# 1 like
				likes = 1
			else:
				# Liked by <> others
				likes = int(browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div/a/span').get_attribute('innerHTML'))
			date = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/div/div/time').get_attribute('title')
		# Handle videos
		else:
			post_type = 'video'
			if isXPATHPresent(browser, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/span/span'):
				views_element = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/span/span')
				views = int(views_element.get_attribute('innerHTML'))
				views_element.click()
				likes = int(browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div/div[4]/span').get_attribute('innerHTML'))
				date = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[2]/a/time').get_attribute('title')
			# Some videos are inconsistent and do not display views (structured as images, possibly uploaded as gifs?)
			else:
				# No view information for posts of this type
				views = None
				caption = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span').get_attribute('innerHTML')
				if isXPATHPresent(browser, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/span/a'):
					likes = 1
					if isXPATHPresent(browser, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/a/span'):
						likes += int(browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/a/span').get_attribute('innerHTML'))
				else:
					likes = int(browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div/a/span').get_attribute('innerHTML'))
				date = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/div/div/time').get_attribute('title')
		
		cleaned = {"post_type": post_type, "caption": caption, "likes": likes, "views": views, "date": date}
		cleaned_posts.append(cleaned)

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
