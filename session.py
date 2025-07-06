import logging

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.util.retry import Retry


class ModSession(Session):
    def __init__(self, imageboard, username, password, retries=3, timeout=10, backoff_factor=0.3, http_username=None, http_password=None):
        super().__init__()
        self.imageboard = imageboard
        self.imageboard_url = f"https://{imageboard}"
        self.http_username = http_username
        self.http_password = http_password
        if http_username is not None and http_password is not None:
            self.auth = HTTPBasicAuth(http_username, http_password)
        self.auth_params = {'username': username, 'password': password}
        self.csrf_token = None

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

    def update_csrf(self):
        try:
            res = self.get(url=f'{self.imageboard_url}/csrf.json',
                headers={'Referer': f'{self.imageboard_url}/csrf.json'}).json()
            if 'token' in res:
                self.csrf_token = res['token']
            else:
                raise Exception('Unable to update csrf token')
        except requests.RequestException as e:
            logging.error(f'Exception {e} occurred while updating csrf token')
            raise Exception('Unable to update csrf token')

    def post_actions(self, **kwargs):
        try:
            actions = kwargs['actions'].split(',')
            body = {'checkedposts':kwargs["postid"],'_csrf':self.csrf_token,'log_message':'globalafk'}
            for action in actions:
                body[action] = '1'
            res = self.post(url=f'{self.imageboard_url}/forms/board/{kwargs["board"]}/modactions',
                headers={'Referer': f'{self.imageboard_url}/forms/board/{kwargs["board"]}/modactions','x-using-xhr': 'true'},
                data=body).json()
            return res
        except requests.RequestException as e:
            logging.error(f'Exception {e} occurred while posting action')
            raise Exception('Failed to submit post actions')
