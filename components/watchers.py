import logging
from abc import ABC
from threading import Thread, Event

import socketio
from requests import RequestException


def get_path(post): return f'>>>/{post["board"]}/{post["thread"] or post["postId"]} ({post["postId"]})'


class Watcher(ABC, Thread):
    def __init__(self, session):
        Thread.__init__(self)
        self.daemon = True
        self._stp = Event()  # _stop is reserved
        self.session = session

    def stop(self):
        logging.debug(f'Killing thread, goodbye')
        self._stp.set()


class RecentWatcher(Watcher):
    def __init__(self, session, notify, evaluate, board=None, reconnection_delay=15):
        super().__init__(session)

        client = socketio.Client(  # cannot use class variable to make the annotations
            http_session=session,
            reconnection_delay=reconnection_delay,
            reconnection_delay_max=reconnection_delay
        )

        @client.event
        def connect():
            logging.debug(f'Live posts client connected')
            client.emit('room', f'{board}-manage-recent-hashed' if board else 'globalmanage-recent-hashed')
            notify(f'Connected', f'Watching live posts')

        @client.event
        def disconnect():
            logging.error(f'Live posts client disconnected')
            notify(f'Lost live posts connection', f'Retrying in {reconnection_delay} seconds')

        @client.on('newPost')
        def on_new_post(post):
            urls, entries = evaluate(post["nomarkup"])
            if urls or entries:
                notify(f'Alert! {get_path(post)}', '\n'.join(urls) + '\n'.join(entries))

        self.client = client
        self.start()

    def run(self):
        self.client.connect(f'wss://{self.session.imageboard}/')
        self.client.wait()  # blocks the thread until something happens

        if self._stp.wait():
            logging.info("Exiting recent watcher")
            self.client.disconnect()


class ReportsWatcher(Watcher):
    def __init__(self, session, notify, board=None, fetch_interval=60 * 2):
        super().__init__(session)
        self.notify = notify
        self.fetch_interval = fetch_interval

        self._endpoint = f'{session.imageboard_url}/{f"{board}/manage" if board else "globalmanage"}/reports.json'
        self.known_reports = 0

        self.start()

    def fetch_reports(self):
        reports = self.session.get(url=self._endpoint).json()["reports"]
        return reports, len(reports)

    def run(self):
        while True:  # main loop, do while bootleg
            try:
                reported_posts, num_reported_posts = self.fetch_reports()
                if 0 < num_reported_posts != self.known_reports:
                    self.notify(f'New reports!', "\n".join([
                        f'{get_path(p)}  {[r["reason"] for r in (p["globalreports"] if "globalreports" in p else p["reports"])]}'
                        for p in reported_posts]))

                self.known_reports = num_reported_posts

            except RequestException as e:
                logging.error(f'Exception {e} occurred while fetching reports')
                self.notify(f'Error while fetching reports', f'Trying to reconnect')

            if self._stp.wait(self.fetch_interval):
                logging.info("Exiting reports watcher")
                break
