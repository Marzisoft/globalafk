import logging
import subprocess
import time
from threading import Thread

import requests
import socketio

from config import config
from evaluator import Evaluator


def get_path(post): return f'>>>/{post["board"]}/{post["thread"] or post["postId"]} ({post["postId"]})'


def send_notification(title, body):
    logging.debug(f'Sending notification: {title} {body}')

    subprocess.call(['termux-notification', '--title', title, '--content', body] if config.USE_TERMUX_API
                    else ['notify-send', title, body])


def watch_live_posts(evaluate, notify):
    def get_auth_cookie():
        logging.debug('Requesting new cookie to watch live posts')

        return requests.post(
            url=f'https://{config.IB_DOMAIN_NAME}/forms/login',
            data={'username': config.GLOBAL_MOD_USERNAME, 'password': config.GLOBAL_MOD_PASSWORD},
            headers={'Referer': f'https://{config.IB_DOMAIN_NAME}/login.html'}
        ).headers['set-cookie'].split(';')[0]

    client = socketio.Client(reconnection=False)

    @client.on('newPost')
    def on_new_post(post):
        urls, entries = evaluate(post["nomarkup"])
        if urls or entries:
            notify(f'Alert! {get_path(post)}', '\n'.join(urls) + '\n'.join(entries))

    while True:
        try:
            client.connect(f'wss://{config.IB_DOMAIN_NAME}/', headers={'Cookie': get_auth_cookie()})
            client.emit('room', 'globalmanage-recent-hashed')
        except Exception as e:
            logging.error(f'Exception in live posts watcher: {e}')

            notify(f'Lost live posts connection', f'Retrying in {config.LIVE_POSTS_RETRY_TIMEOUT} seconds')
            time.sleep(config.LIVE_POSTS_RETRY_TIMEOUT)  # waits for a bit, maybe will fix itself

        notify(f'Connected', f'Watching live posts')
        client.wait()  # blocks the thread until something happens


def watch_reports(notify):
    def get_auth_session():
        logging.debug('Starting new authenticated session to fetch reports')

        s = requests.Session()
        s.post(
            url=f'https://{config.IB_DOMAIN_NAME}/forms/login',
            data={'username': config.GLOBAL_MOD_USERNAME, 'password': config.GLOBAL_MOD_PASSWORD},
            headers={'Referer': f'https://{config.IB_DOMAIN_NAME}/login.html'}
        )

        return s

    session = get_auth_session()
    previous = 0
    while True:
        time.sleep(config.FETCH_REPORTS_INTERVAL)
        reply = session.get(f'https://{config.IB_DOMAIN_NAME}/globalmanage/reports.json')

        if reply.status_code != 200:
            logging.error(f'Error while fetching reports: {reply.status_code}')
            notify(f'Error while fetching reports', f'Retrying in {config.FETCH_REPORTS_INTERVAL} seconds')
            session = get_auth_session()
            continue

        reported_posts = reply.json()["reports"]
        current = len(reported_posts)
        if 0 < current != previous:
            notify(f'New reports!',
                   "\n".join([f'{get_path(p)}  {[r["reason"] for r in p["globalreports"]]}' for p in reported_posts]))

        previous = current


def main():
    logging.basicConfig(level=logging.DEBUG)

    # launches live posts watcher
    live_posts_watcher = Thread(target=watch_live_posts, args=(Evaluator().evaluate, send_notification,))
    live_posts_watcher.daemon = True
    live_posts_watcher.start()

    # launches reports watcher
    reports_watcher = Thread(target=watch_reports, args=(send_notification,))
    reports_watcher.daemon = True
    reports_watcher.start()

    live_posts_watcher.join()
    reports_watcher.join()


if __name__ == '__main__':
    main()
