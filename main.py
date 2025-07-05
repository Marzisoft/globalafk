import logging

from config import config
from session import ModSession
from components.watchers import ReportsWatcher, RecentWatcher
from components.notifiers import TermuxNotifier, NotifySendNotifier, AtomFeedBuilder, DiscordNotifier
from components.evaluators import PostEvaluator


def format_match(match):
    s, e = match.start(0), match.end(0)
    m = match.string[:s] + config.TRIGGER_WRAPPER + match.string[s:e] + config.TRIGGER_WRAPPER + match.string[e:]
    return m[s - config.TRIGGER_OFFSET or 0:e if e + config.TRIGGER_OFFSET > len(m) else e + config.TRIGGER_OFFSET]

def multi_notify(notifiers):
    def notify(title, content, *args, **kwargs):
        for notifier in notifiers:
            notifier.notify(title, content, *args, **kwargs)
    return notify

def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s %(funcName)s] %(message)s (%(name)s)')

    session = ModSession(imageboard=config.IMAGEBOARD, username=config.ACCOUNT_USERNAME,
                         password=config.ACCOUNT_PASSWORD, retries=config.REQUEST_RETRIES,
                         timeout=config.REQUEST_TIMEOUT, backoff_factor=config.RETRIES_BACKOFF_FACTOR)

    # notifier = TermuxNotifier() if config.USE_TERMUX_API else NotifySendNotifier()

    imageboardUrl = f"https://{config.IMAGEBOARD}"

    reportsAtomNotifier = AtomFeedBuilder(
            config.REPORTS_FEED_URL,
            config.REPORTS_FEED_TITLE,
            config.FEED_AUTHOR_NAME,
            config.REPORTS_FEED_URL,
            imageboardUrl,
            config.FEED_LOGO,
            config.REPORTS_FEED_SUBTITLE,
            config.FEED_LANGUAGE,
            config.REPORTS_FEED_PATH)

    recentAtomNotifier = AtomFeedBuilder(
            config.RECENT_FEED_URL,
            config.RECENT_FEED_TITLE,
            config.FEED_AUTHOR_NAME,
            config.RECENT_FEED_URL,
            imageboardUrl,
            config.FEED_LOGO,
            config.RECENT_FEED_SUBTITLE,
            config.FEED_LANGUAGE,
            config.RECENT_FEED_PATH)

    recentDiscordNotifier = DiscordNotifier(config.RECENT_WEBHOOK)
    reportsDiscordNotifier = DiscordNotifier(config.REPORTS_WEBHOOK)

    recentNotify = multi_notify([
        recentAtomNotifier,
        recentDiscordNotifier])
    reportsNotify = multi_notify([
        reportsAtomNotifier,
        reportsDiscordNotifier])

    watchers = list()
    for board in config.REPORTS_BOARDS:
        if config.WATCH_REPORTS:  # launches reports watcher
            watchers.append(ReportsWatcher(session=session, notify=reportsNotify, board=board,
                                           fetch_interval=config.FETCH_REPORTS_INTERVAL))
    for board in config.RECENT_BOARDS:
        if config.WATCH_RECENT:  # launches recent watcher
            watchers.append(RecentWatcher(session=session, notify=recentNotify, board=board,
                                          evaluate=lambda p: (True, True)))
    for watcher in watchers:
        watcher.join()


if __name__ == '__main__':
    main()
