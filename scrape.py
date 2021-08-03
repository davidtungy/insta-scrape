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
