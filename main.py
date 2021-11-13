import logging

from config import config
from session import ModSession
from watchers import ReportsWatcher, RecentWatcher
from notifiers import TermuxNotifier, NotifySendNotifier
from evaluators import PostEvaluator


def main():
    # filename = "log.log", filemode = 'a'
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s %(funcName)s] %(message)s (%(name)s)')

    session = ModSession(imageboard=config.IMAGEBOARD, username=config.ACCOUNT_USERNAME,
                         password=config.ACCOUNT_PASSWORD, retries=config.REQUEST_RETRIES,
                         timeout=config.REQUEST_TIMEOUT, backoff_factor=config.RETRIES_BACKOFF_FACTOR)

    notifier = TermuxNotifier() if config.USE_TERMUX_API else NotifySendNotifier()

    watchers = list()
    for board in config.BOARDS:
        if config.WATCH_REPORTS:  # launches reports watcher
            watchers.append(ReportsWatcher(session=session, notify=notifier.notify, board=board,
                                           fetch_interval=config.FETCH_REPORTS_INTERVAL))
        if config.WATCH_RECENT:  # launches recent watcher
            watchers.append(RecentWatcher(session=session, notify=notifier.notify, board=board,
                                          evaluate=PostEvaluator(blacklist=config.BLACKLIST,
                                                                 url_whitelist=config.URL_WHITELIST).eval))
    for watcher in watchers:
        watcher.join()


if __name__ == '__main__':
    main()
