import logging
import subprocess

from config import config
from evaluator import Evaluator
from session import ModSession
from watchers import ReportsWatcher, LivePostsWatcher


def send_notification(title, body):
    logging.debug(f'Sending notification with title: {title} and body: {body}')
    subprocess.call(['termux-notification', '--title', title, '--content', body] if config.USE_TERMUX_API
                    else ['notify-send', title, body])


def main():
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s %(funcName)s] %(message)s (%(name)s)')
    session = ModSession()  # custom session that is authenticated and hopefully can be shared between watchers
    watchers = list()
    if config.WATCH_REPORTS:  # launches reports watcher
        watchers.append(ReportsWatcher(session, send_notification))
    if config.WATCH_LIVE_POSTS:  # launches live posts watcher
        watchers.append(LivePostsWatcher(session, send_notification, Evaluator().evaluate))
    for watcher in watchers:
        watcher.join()


if __name__ == '__main__':
    main()
