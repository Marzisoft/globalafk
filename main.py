import logging
import subprocess

from config import config
from evaluator import Evaluator
from session import ModSession
from watchers import ReportsWatcher, LivePostsWatcher


def send_notification(title, body):
    logging.debug(f'Sending notification: {title} {body}')
    subprocess.call(['termux-notification', '--title', title, '--content', body] if config.USE_TERMUX_API
                    else ['notify-send', title, body])


def main():
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s %(funcName)s] %(message)s (%(name)s)')

    session = ModSession()  # custom session that is authenticated and hopefully can be shared between watchers
    reports_watcher = ReportsWatcher(session, send_notification)  # launches reports watcher
    live_posts_watcher = LivePostsWatcher(session, send_notification,
                                          Evaluator().evaluate)  # launches live posts watcher

    reports_watcher.join()
    live_posts_watcher.join()


if __name__ == '__main__':
    main()
