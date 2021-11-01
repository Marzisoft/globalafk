IMAGEBOARD: str = "dummy.ib"
ACCOUNT_USERNAME: str = "dummy_username"
ACCOUNT_PASSWORD: str = "dummy_password"
BOARDS: tuple = (  # None if global or boards that you moderate
    'dummy',  # /dummy/ board entry
)

"""Notifications"""
USE_TERMUX_API: bool = False

"""Reports watcher """
WATCH_REPORTS: bool = True
FETCH_REPORTS_INTERVAL: int = 60 * 2  # interval between reports fetch (in seconds)

"""Recent watcher"""
WATCH_RECENT: bool = True
RECENT_RECONNECTION_DELAY: int = 25  # delay between live posts socket reconnection (in seconds)

# posts text match
BLACKLIST: tuple = (  # or None to turn off blacklist (each entry must be a regex)
    r"\bd+u+m+m+y*\b",
)
TRIGGER_OFFSET: int = 25  # number of characters showed before/after the trigger
TRIGGER_WRAPPER: str = "*"  # string used to wrap the *trigger*

# posts url match
URL_WHITELIST: tuple = (  # or None to turn off url blacklist (each entry must be a regex)
    r"(\w*:/+)*(\w*\.)*(dummy.com)(/+\w*)*",

)

"""Custom session related, conservative values by default"""
REQUEST_RETRIES: int = 6  # number of allowed retries
RETRIES_BACKOFF_FACTOR: float = 3  # sleep factor between retries, defines how the backoff grows
REQUEST_TIMEOUT: int = 15  # max wait time for a server response (in seconds)
