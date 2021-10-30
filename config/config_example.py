DOMAIN_NAME: str = "dummy.ib"
ACCOUNT_USERNAME: str = "dummy_username"
ACCOUNT_PASSWORD: str = "dummy_password"
TARGET_BOARDS: tuple = (  # None if global or boards that you moderate
    'dummy',  # /dummy/ board entry
)

"""Notification related"""
USE_TERMUX_API: bool = False

"""Reports watcher related"""
WATCH_REPORTS: bool = True
FETCH_REPORTS_INTERVAL: int = 60 * 2  # interval between reports fetch (in seconds)

"""Posts watcher related"""
WATCH_LIVE_POSTS: bool = True
LIVE_POSTS_RECONNECT_DELAY: int = 25  # delay between live posts socket reconnection (in seconds)

# live posts text matches related
TRIGGER_ON_BLACKLISTED: bool = True  # text that are blacklisted entries should trigger a notification?
TRIGGER_OFFSET: int = 25  # number of characters showed before/after the trigger
TRIGGER_WRAPPER: str = "*"  # string used to wrap the *trigger*
BLACKLIST: tuple = (  # each entry must be a regex
    r"\bd+u+m+m+y*\b",
)
# live post url matches related
TRIGGER_ON_NON_WHITELISTED_URLS: bool = False  # urls that are not whitelisted should trigger a notification?
URL_WHITELIST: tuple = (  # each entry must be a regex
    r"(\w*:/+)*(\w*\.)*(dummy.com)(/+\w*)*",

)

"""Custom session related, conservative values by default"""
REQUEST_RETRIES: int = 6  # number of allowed retries
RETRIES_BACKOFF_FACTOR: float = 3  # sleep factor between retries, defines how the backoff grows
REQUEST_TIMEOUT: int = 15  # max wait time for a server response (in seconds)
