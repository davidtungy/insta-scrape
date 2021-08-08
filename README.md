# insta-scrape

Selenium/Beautiful Soup Instagram web scraper.

Authenticates via user-supplied log in credentials or local cookie cache and pulls in data from a configurable amount of available posts. Potential use cases include:

- User engagement metric reporting and visualization
- Instagram post analysis (topic models, frequency, engagement correlation)
- Consolidate both metrics and analysis into an automated test report

# Usage

```
python scrape.py [-h] [-u USER] [-p PASSWORD] username

positional arguments:
  username              Instagram username to process.

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  Your Instagram user login. Used to scrape private accounts (must be a follower).
  -p PASSWORD, --password PASSWORD
                        Your Instagram user password. Used to scrape private accounts (must be a follower).
```

# Details

## Terminology

@username: Instagram username to process

user:     Your Instagram username login

password: Your Instagram username password

## scrape.py

Contains logic to scrape a given username's posts.

### Flow: 

1. Load up a Selenium webdriver
2. Authenticate via log-in (user and password) or cached information
3. Get @username's follower counts (number of followers and number of accounts @username is following)
4. Get URLs of @username's posts either by scraping or via local cache.
5. Access saved URLs and saves post information locally (for analysis)

### Output fields: 

| Field | Type | Description |
| --- | --- | --- |
| caption | String | Instagram caption |
| post_type | String | 'image' or 'video' |
| views | integer | Number of views of video post |
| likes | integer | Number of likes on the post |
| date | String | Date of post (e.g. Jul 30, 2021) |
