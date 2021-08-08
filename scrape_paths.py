COOKIE_PATH				= 'cookie.pkl'
LOGIN_URL				= 'https://www.instagram.com/accounts/login/?hl=en'
INSTAGRAM_TEMPLATE		= 'https://www.instagram.com{}?hl=en'

BODY 					= '//body'

# Login xpaths
LOGIN_FIELD_USERNAME	= '//*[@id="loginForm"]/div/div[1]/div/label/input'
LOGIN_FIELD_PASSWORD	= '//*[@id="loginForm"]/div/div[2]/div/label/input'
LOGIN_FIELD_SUBMIT		= '//*[@id="loginForm"]/div/div[3]/button'
LOGIN_INCORRECT			= '//*[@id="slfErrorAlert"]'
LOGIN_LOGIN_SAVE 		= '//*[@id="react-root"]/section/main/div/div/div/div/button'
LOGIN_NOTIFICATIONS_1	= '/html/body/div[4]/div/div/div/div[3]/button[2]'
LOGIN_NOTIFICATIONS_2	= '/html/body/div[5]/div/div/div/div[3]/button[2]'
LOGIN_NOTIFICATIONS_3	= '/html/body/div[6]/div/div/div/div[3]/button[2]'

# Used to detect incorrect viewing permissions
INVALID_USER			= '//*[@id="react-root"]/section/main/div/div/div/div/a'
PRIVATE_PROFILE			= '//*[@id="react-root"]/section/main/div/div/article/div/div/h2'

FOLLOWERS_COUNT			= '//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a/span'
FOLLOWING_COUNT			= '//*[@id="react-root"]/section/main/div/header/section/ul/li[3]/a/span'

# JavaScript to execute
JS_GET_SCROLL_HEIGHT	= 'return document.body.scrollHeight'
JS_SCROLL_TO_BOTTOM		= 'window.scrollTo(0, document.body.scrollHeight);'

# Selector for post div (group of 3)
POST_DIV				= 'div.v1Nh3.kIKUG._bz0w'

# Post details xpaths
CAPTION					= '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span'

IMAGE_LIKED_BY_X		= '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/span/a'
IMAGE_LIKED_BY_X_AND_OTHERS	= '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div[2]/a/span'
IMAGE_ONE_LIKE			= '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div/a'
IMAGE_LIKED_BY_OTHERS 	= '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div/a/span'
IMAGE_DATE					= '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/div/div/time'

VIDEO_VIEWS				= '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/span/span'
VIDEO_LIKES				= '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[2]/div/div/div[4]/span'
VIDEO_DATE				= '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[2]/a/time'






