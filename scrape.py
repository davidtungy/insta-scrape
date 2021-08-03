import time

import argparse
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

def main(args):
	options = webdriver.ChromeOptions()
	options.add_argument('--ignore-certificate-errors')
	options.add_argument('--incognito')
	#options.add_argument('--headless')
	browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
	time.sleep(1)
	soup = BeautifulSoup(browser.page_source, 'lxml')

	authenticate(browser, args.user, args.password)

	followers, following = getFollowCounts(browser, args.username)
	print("My boy has", followers, "followers and is following", following)
	print("Follow ratio of ", followers/following)

	scroll_to_bottom(browser)
	element = browser.find_element_by_xpath("//body").get_attribute('outerHTML')
	soup = BeautifulSoup(element, 'html.parser')
	posts = soup.select('div.v1Nh3.kIKUG._bz0w')
	print("Found ", len(posts), " posts to scrutinize")

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
	if isXPATHPresent(browser, '/html/body/div[4]/div/div/div/div[3]/button[2]'):
		browser.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div[3]/button[2]').click()
	else:
		browser.find_element(By.XPATH, '/html/body/div[5]/div/div/div/div[3]/button[2]').click()
	time.sleep(1)

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
# Added a max scroll count (if someone has a crazy amount of posts)
def scroll_to_bottom(browser):
	prev = browser.execute_script("return document.body.scrollHeight")
	max_count = 5
	curr_count = 0
	while True:
		browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(2)
		curr = browser.execute_script("return document.body.scrollHeight")
		curr_count += 1
		if curr == prev or curr_count >= max_count:
			break
		prev = curr


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
