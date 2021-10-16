IB_DOMAIN_NAME = "dummy.ib"
GLOBAL_MOD_USERNAME = "dummy_username"
GLOBAL_MOD_PASSWORD = "dummy_password"

LIVE_POSTS_RETRY_TIMEOUT = 25  # seconds
FETCH_REPORTS_INTERVAL = 60 * 2  # seconds

USE_TERMUX_API = False

BLACKLIST = (
    r"\bd+u+m+m+y*\b",
)

URL_WHITELIST = (
    r"(\w*:/+)*(\w*\.)*(dummy.com)(/+\w*)*",
)
