DOMAIN_NAME: str = "dummy.ib"
MOD_USERNAME: str = "dummy_username"
MOD_PASSWORD: str = "dummy_password"

"""Custom session related, conservative values by default"""
REQUEST_RETRIES: int = 6  # number of allowed retries
RETRIES_BACKOFF_FACTOR: float = 3  # sleep factor between retries, defines how the backoff grows
REQUEST_TIMEOUT: int = 15  # max wait time for a server response (in seconds)

"""Notification related"""
USE_TERMUX_API: bool = False

"""Reports watcher related"""
FETCH_REPORTS_INTERVAL: int = 60 * 2  # interval between reports fetch (in seconds)

"""Live posts watcher related"""
LIVE_POSTS_RECONNECT_DELAY: int = 25  # delay between live posts socket reconnection (in seconds)

"""Live posts evaluator related"""
# text matches related
TRIGGER_ON_BLACKLISTED: bool = True  # text that are blacklisted entries should trigger a notification?
TRIGGER_OFFSET: int = 25  # number of characters showed before/after the trigger
TRIGGER_WRAPPER: str = "*"  # string used to wrap the *trigger*
BLACKLIST: tuple = (  # each entry must be a regex
    r"\bd+u+m+m+y*\b",
)
# urls matches related
TRIGGER_ON_NON_WHITELISTED_URLS: bool = False  # urls that are not whitelisted should trigger a notification?
URL_WHITELIST: tuple = (  # each entry must be a regex
    r"(\w*:/+)*(\w*\.)*(dummy.com)(/+\w*)*",

)
