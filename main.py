import logging
import subprocess

from config import config
from evaluator import PostEvaluator
from session import ModSession
from watchers import ReportsWatcher, RecentWatcher


def send_notification(title, body):
    logging.debug(f'Sending notification with title: {title} and body: {body}')
    subprocess.call(['termux-notification', '--title', title, '--content', body] if config.USE_TERMUX_API
                    else ['notify-send', title, body])


def main():
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s %(funcName)s] %(message)s (%(name)s)')

    session = ModSession(  # custom session that is authenticated and hopefully can be shared between watchers
        imageboard=config.IMAGEBOARD,
        username=config.ACCOUNT_USERNAME,
        password=config.ACCOUNT_PASSWORD,
        retries=config.REQUEST_RETRIES,
        timeout=config.REQUEST_TIMEOUT,
        backoff_factor=config.RETRIES_BACKOFF_FACTOR
    )

    watchers = list()
    if config.BOARDS:
        for board in config.BOARDS:
            if config.WATCH_REPORTS:  # launches reports watcher
                watchers.append(ReportsWatcher(
                    session=session,
                    notify=send_notification,
                    board=board,
                    fetch_interval=config.FETCH_REPORTS_INTERVAL
                ))
            if config.WATCH_RECENT:  # launches live posts watcher
                watchers.append(RecentWatcher(
                    session=session,
                    notify=send_notification,
                    board=board,
                    evaluate=PostEvaluator(blacklist=config.BLACKLIST, url_whitelist=config.URL_WHITELIST).evaluate
                ))

    else:
        if config.WATCH_REPORTS:  # launches reports watcher
            watchers.append(ReportsWatcher(
                session=session,
                notify=send_notification,
                fetch_interval=config.FETCH_REPORTS_INTERVAL
            ))

        if config.WATCH_RECENT:  # launches live posts watcher
            watchers.append(RecentWatcher(
                session=session,
                notify=send_notification,
                evaluate=PostEvaluator(blacklist=config.BLACKLIST, url_whitelist=config.URL_WHITELIST).evaluate
            ))

    for watcher in watchers:
        watcher.join()


if __name__ == '__main__':
    main()
