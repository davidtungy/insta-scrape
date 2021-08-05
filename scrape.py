import time

import argparse
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pickle
from os import path
import os

COOKIE_PATH = 'cookie.pkl'

def main(args):
	options = webdriver.ChromeOptions()
	options.add_argument('--ignore-certificate-errors')
	#options.add_argument('--incognito')
	#options.add_argument('--headless')
	browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
	time.sleep(1)
	soup = BeautifulSoup(browser.page_source, 'lxml')

	# Use cookie if available (don't want to get timeout banned)
	if path.exists(COOKIE_PATH):
		# Must navigate to same domain
		page_url = 'https://www.instagram.com/accounts/login/?hl=en'
		browser.get(page_url)
		with open(COOKIE_PATH, 'rb') as cookiesfile:
			cookies = pickle.load(cookiesfile)
			for cookie in cookies:
				browser.add_cookie(cookie)
	elif args.user is not None and args.password is not None:
		authenticate(browser, args.user, args.password)

	followers, following = getFollowCounts(browser, args.username)
	print("My boy has", followers, "followers and is following", following)
	print("Follow ratio of ", followers/following)

	urls = getPostUrls(browser, max_posts=500)
	print("---")
	print(len(urls), " posts to scrutinize...")
	print(urls)

	time.sleep(2000)
	browser.quit()

def authenticate(browser, username, password):
	login_url = page_url = 'https://www.instagram.com/accounts/login/?hl=en'
	browser.get(page_url)
	time.sleep(1)
	browser.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input').send_keys(username)
	browser.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input').send_keys(password)
	time.sleep(1)
	browser.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[3]/button').click()
	time.sleep(5)
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
	# save cookie
	print("Cookies:", browser.get_cookies())
	with open(os.path.join(os.path.dirname(__file__), COOKIE_PATH), 'wb') as filehandler:
		pickle.dump(browser.get_cookies(), filehandler)

def isXPATHPresent(browser, xpath):
	return len(browser.find_elements(By.XPATH, xpath)) > 0

def getFollowCounts(browser, user):
	page_url = 'https://www.instagram.com/{}/?hl=en'.format(user)
	browser.get(page_url)
	time.sleep(5)
	followers = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span').get_attribute('innerHTML')
	followers = int(followers.replace(',', '').strip())
	following = browser.find_element(By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/span').get_attribute('innerHTML')
	following = int(following.replace(',', '').strip())
	return followers, following
	
# Scroll to bottom of the browser to pick up dynamically-loaded content
# A maximum of 32 posts or so can be displayed at a time
# Added a max post count (if someone has a crazy amount of posts)
# Returns individual post urls in chronological order (oldest first)
def getPostUrls(browser, max_posts=100, timeout=4):
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
	return urls


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
