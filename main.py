import logging

from config import config
from session import ModSession
from components.watchers import ReportsWatcher, RecentWatcher
from components.notifiers import TermuxNotifier, NotifySendNotifier
from components.evaluators import PostEvaluator


def format_match(match):
    s, e = match.start(0), match.end(0)
    m = match.string[:s] + config.TRIGGER_WRAPPER + match.string[s:e] + config.TRIGGER_WRAPPER + match.string[e:]
    return m[s - config.TRIGGER_OFFSET or 0:e if e + config.TRIGGER_OFFSET > len(m) else e + config.TRIGGER_OFFSET]


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s %(funcName)s] %(message)s (%(name)s)')

    session = ModSession(imageboard=config.IMAGEBOARD, username=config.ACCOUNT_USERNAME,
                         password=config.ACCOUNT_PASSWORD, retries=config.REQUEST_RETRIES,
                         timeout=config.REQUEST_TIMEOUT, backoff_factor=config.RETRIES_BACKOFF_FACTOR)

    # notifier = TermuxNotifier() if config.USE_TERMUX_API else NotifySendNotifier()

    imageboardUrl = f"https://{config.IMAGEBOARD}"

    reportsNotifier = AtomFeedBuilder(
            config.REPORTS_FEED_URL,
            config.REPORTS_FEED_TITLE,
            config.FEED_AUTHOR_NAME,
            config.REPORTS_FEED_URL,
            imageboardUrl,
            config.FEED_LOGO,
            config.REPORTS_FEED_SUBTITLE,
            config.FEED_LANGUAGE,
            config.REPORTS_FEED_PATH)

    recentNotifier = AtomFeedBuilder(
            config.RECENT_FEED_URL,
            config.RECENT_FEED_TITLE,
            config.FEED_AUTHOR_NAME,
            config.RECENT_FEED_URL,
            imageboardUrl,
            config.FEED_LOGO,
            config.RECENT_FEED_SUBTITLE,
            config.FEED_LANGUAGE,
            config.RECENT_FEED_PATH)

    watchers = list()
    for board in config.BOARDS:
        if config.WATCH_REPORTS:  # launches reports watcher
            watchers.append(ReportsWatcher(session=session, notify=reportsNotifier.notify, board=board,
                                           fetch_interval=config.FETCH_REPORTS_INTERVAL))
        if config.WATCH_RECENT:  # launches recent watcher
            watchers.append(RecentWatcher(session=session, notify=recentNotifier.notify, board=board,
                                          evaluate=PostEvaluator(blacklist=config.BLACKLIST,
                                                                 url_whitelist=config.URL_WHITELIST).eval))
    for watcher in watchers:
        watcher.join()


if __name__ == '__main__':
    main()
