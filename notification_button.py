import logging
import subprocess

import sys, getopt
from config import config
from session import ModSession

def main(argv):
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s %(funcName)s] %(message)s (%(name)s)')

    try:
        opts, args = getopt.getopt(argv, 'b:p:a:', ['board=', 'postid=', 'actions='])
        optdict = dict(opts)
    except getopt.GetoptError:
        logging.error('invalid arguments')
        sys.exit(1)

    session = ModSession(imageboard=config.IMAGEBOARD, username=config.ACCOUNT_USERNAME,
                         password=config.ACCOUNT_PASSWORD, retries=config.REQUEST_RETRIES,
                         timeout=config.REQUEST_TIMEOUT, backoff_factor=config.RETRIES_BACKOFF_FACTOR)

    session.update_csrf()

    res = session.post_actions(board=optdict['-b'], postid=optdict['-p'], actions=optdict['-a'])
    if 'message' in res:
        subprocess.call(['termux-toast', res['message']])

if __name__ == '__main__':
    main(sys.argv[1:])
