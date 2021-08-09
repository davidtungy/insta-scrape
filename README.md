# insta-scrape

Selenium/Beautiful Soup Instagram web scraper. Contains supplemental code to visualize and analyze caption data.

Authenticates via user-supplied log in credentials or local cookie cache and pulls in data from a configurable amount of available posts. Potential use cases include:

- User engagement metric reporting and visualization
- Instagram post analysis (topic models, frequency, engagement correlation)
- Consolidate both metrics and analysis into an automated report

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

```
usage: analysis.py [-h] username

positional arguments:
  username    Instagram username to process. Expects to find output of
              scrape.py (<username>.csv) at ./<username>

optional arguments:
  -h, --help  show this help message and exit
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

## scrape.py

Analyzes a given username's posts (must run scrape.py prior). Performs text cleaning from raw HTML input. 

Charts and saves the following information locally:
- Likes over time (likes.png)
- Wordcloud of commonly used phrases (wordcloud.png)
- LDA visualization of topics, via pyLDAvis (lda.html)
- Topic clustering from optimal LDA grouping based on penalized-coherence score (topics.png)
