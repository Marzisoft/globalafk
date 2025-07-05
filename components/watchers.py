import logging
from abc import ABC
from threading import Thread, Event

import socketio
from requests import RequestException

import base64

def get_quote(post): return f'/{post["board"]}/{post["postId"]}'

def get_manage_path(post): return f'/{post["board"]}/manage/thread/{post["thread"] or post["postId"]}.html#{post["postId"]}'

def get_post_path(post): return f'/{post["board"]}/thread/{post["thread"] or post["postId"]}.html#{post["postId"]}'

def get_report_path(post, isGlobal): return f'/globalmanage/reports.html' if isGlobal else f'/{post["board"]}/manage/reports.html'

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

        @client.event
        def disconnect():
            logging.error(f'Live posts client disconnected')

        @client.on('newPost')
        def on_new_post(post):
            urls, entries = evaluate(post["nomarkup"])
            if urls or entries:
                post_url=f'{session.imageboard_url}{get_post_path(post)}'
                buttons=[{"text":"Delete","actions":"delete"},
                    {"text":"Delete+Ban" if board else "Delete+Global Ban","actions":"delete,ban" if board else "delete,global_ban"}]
					#todo: add this last button even if a board recents, because global staff can still global ban. but need a way to
					#check if the account is global staff, which we dont have a json endpoint for in jschan yet.
                    #{"text":"Delete+Global Ban","actions":"dismiss" if board else "global_dismiss"}]
                notify(f'New Post: {get_quote(post)}', post['nomarkup'], link=post_url, post=post, buttons=buttons)

        self.client = client
        self.start()

    def run(self):
        self.client.connect(f'wss://{self.session.imageboard}/', transports=['websocket'])
        self.client.wait()  # blocks the thread until something happens

        if self._stp.wait():
            logging.info("Exiting recent watcher")
            self.client.disconnect()


class ReportsWatcher(Watcher):
    def __init__(self, session, notify, board=None, fetch_interval=60 * 2):
        super().__init__(session)
        self.notify = notify
        self.fetch_interval = fetch_interval

        self.board = board
        self._endpoint = f'{session.imageboard_url}/{f"{board}/manage" if board else "globalmanage"}/reports.json'
        self.known_reports = set()

        self.start()

    def fetch_reports(self):
        reports = self.session.get(url=self._endpoint).json()["reports"]
        return reports, len(reports)

    def run(self):
        while True:  # main loop, do while bootleg
            try:
                reported_posts, num_reported_posts = self.fetch_reports()
                if 0 < num_reported_posts != self.known_reports:
                    for p in reported_posts:

                        #todo: allow to customise these buttons somewhere
                        buttons=[{"text":"Delete","actions":"delete"},
                            {"text":"Delete+Ban" if self.board else "Delete+Global Ban","actions":"delete,ban" if self.board else "delete,global_ban"},
                            {"text":"Dismiss","actions":"dismiss" if self.board else "global_dismiss"}]

                        if 'globalreports' in p:
                            for r in p['globalreports']:
                                post_url=f'{self.session.imageboard_url}{get_report_path(p, True)}'
                                if r['id'] not in self.known_reports:
                                    self.known_reports.add(r['id'])
                                    self.notify(f'New Report: {get_quote(p)}', f"Reason: {r['reason']}", link=post_url, post=p, uuid=r['id'], buttons=buttons)
                        if 'reports' in p:
                            for r in p['reports']:
                                post_url=f'{self.session.imageboard_url}{get_report_path(p, False)}'
                                if r['id'] not in self.known_reports:
                                    self.known_reports.add(r['id'])
                                    self.notify(f'Report for {get_quote(p)}', r['reason'], link=post_url, post=p, uuid=r['id'], buttons=buttons)

            except RequestException as e:
                logging.error(f'Exception {e} occurred while fetching reports')

            if self._stp.wait(self.fetch_interval):
                logging.info("Exiting reports watcher")
                break
