import logging
from abc import ABC
from threading import Thread, Event

import socketio
from requests import RequestException

from config import config


def get_path(post): return f'>>>/{post["board"]}/{post["thread"] or post["postId"]} ({post["postId"]})'


class Watcher(ABC, Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.kill = Event()

    def kill(self):
        logging.debug(f'Killing thread, goodbye')
        self.kill.set()


class LivePostsWatcher(Watcher):
    def __init__(self, session, notify, evaluate):
        super().__init__()
        self.session = session
        self.evaluate = evaluate
        self.notify = notify

        io = socketio.Client(reconnection=False)  # cannot use class variable to make the annotation

        @io.on('newPost')
        def on_new_post(post):  # specifies new post handler
            urls, entries = evaluate(post["nomarkup"])
            if urls or entries:
                notify(f'Alert! {get_path(post)}', '\n'.join(urls) + '\n'.join(entries))

        self.io = io

        self.start()

    def run(self):
        while True:  # main loop, do while bootleg
            try:
                self.io.connect(f'wss://{config.DOMAIN_NAME}/', headers={'Cookie': self.session.auth_cookie()})
                self.io.emit('room', 'globalmanage-recent-hashed')
                self.notify(f'Connected', f'Watching live posts')

                self.io.wait()  # blocks the thread until something happens
            except Exception as e:
                logging.error(f'Exception occurred {e}while watching live')
                self.notify(f'Lost live posts connection', f'Retrying in {config.LIVE_POSTS_RETRY_TIMEOUT} seconds')

            if not self.kill.wait(config.LIVE_POSTS_RETRY_TIMEOUT):
                break


class ReportsWatcher(Watcher):
    def __init__(self, session, notify):
        super().__init__()
        self.session = session

        self.notify = notify
        self.known_reports = 0

        self.start()

    def fetch_reports(self):
        reply = self.session.get(
            url=f'https://{config.DOMAIN_NAME}/globalmanage/reports.json')
        reply.raise_for_status()
        reports = reply.json()["reports"]
        return reports, len(reports)

    def run(self):
        while True:  # main loop, do while bootleg
            try:
                reported_posts, num_reported_posts = self.fetch_reports()
                if 0 < num_reported_posts != self.known_reports:
                    self.notify(f'New reports!',
                                "\n".join([f'{get_path(p)}  {[r["reason"] for r in p["globalreports"]]}' for p in
                                           reported_posts]))

                self.known_reports = num_reported_posts
            except RequestException as e:
                logging.error(f'Exception {e} occurred while fetching reports')
                self.notify(f'Error while fetching reports', f'Trying to reconnect')

            if not self.kill.wait(config.FETCH_REPORTS_INTERVAL):
                break
