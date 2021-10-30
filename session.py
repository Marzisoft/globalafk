import logging

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from config import config


class ModSession(Session):
    def __init__(self):
        super().__init__()
        self.mount(f'https://{config.DOMAIN_NAME}/',  # overwriting the default adapters to force the config values
                   HTTPAdapter(max_retries=Retry(total=config.REQUEST_RETRIES, backoff_factor=config.REQUEST_RETRIES)))
        self.timeout = config.REQUEST_TIMEOUT
        self.hooks = {
            'response': [lambda response, *args, **kwargs: response.raise_for_status()]}  # always raise for status

        self._auth()  # tries to authenticate the session

    def request(self, method, url, **kwargs):  # overwrites request function to add timeout
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        return super().request(method, url, **kwargs)

    def _auth(self):
        # TODO probably this should be wrapped in cycle that awaits until the problem fixes itself
        try:
            self.post(
                url=f'https://{config.DOMAIN_NAME}/forms/login',
                data={'username': config.ACCOUNT_USERNAME, 'password': config.ACCOUNT_PASSWORD},
                headers={'Referer': f'https://{config.DOMAIN_NAME}/login.html'},
                timeout=config.REQUEST_TIMEOUT
            )
        except requests.RequestException as e:  # ambiguous catch but atm nothing can be done in more specific cases
            logging.error(f'Exception {e} occurred while authenticating mod connection')
            self.close()
            raise Exception('Unable to authenticate')

        logging.info('Established mod authenticated session')

    def auth_cookie(self):
        return f'connect.sid={self.cookies.get("connect.sid", domain=config.DOMAIN_NAME)}'
