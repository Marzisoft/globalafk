import logging

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class ModSession(Session):
    def __init__(self, imageboard, username, password, retries=3, timeout=10, backoff_factor=0.3):
        super().__init__()
        self.domain_name = imageboard
        self.imageboard_url = f"https://{imageboard}"
        self.auth_params = {'username': username, 'password': password}

        # overwrites session default behaviour
        self.mount(self.imageboard_url, HTTPAdapter(max_retries=Retry(total=retries, backoff_factor=backoff_factor)))
        self.hooks = {'response': [lambda response, *args, **kwargs: response.raise_for_status()]}
        self._timeout = timeout

        self.authenticate()  # tries to authenticate the session

    def request(self, method, url, **kwargs):  # overwrites request function to add timeout
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self._timeout
        return super().request(method, url, **kwargs)

    def authenticate(self):
        try:
            self.post(url=f'{self.imageboard_url}/forms/login', data=self.auth_params,
                      headers={'Referer': f'{self.imageboard_url}/login.html'})
        except requests.RequestException as e:  # ambiguous catch but atm nothing can be done in more specific cases
            logging.error(f'Exception {e} occurred while authenticating moderator')
            raise Exception('Unable to authenticate moderator')
