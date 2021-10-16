import logging
import re

from urlextract import URLExtract

from config import config


class Evaluator:

    def __init__(self):
        self.blacklist_re = re.compile('|'.join(config.BLACKLIST), re.IGNORECASE)
        logging.info(f"Compiled blacklist regex: {self.blacklist_re}")

        self.url_blacklist_re = re.compile(f'(?!{"|".join(config.URL_WHITELIST)})',
                                           re.IGNORECASE)  # "inverted" so anything not whitelisted will match it
        logging.info(f"Compiled url blacklist regex: {self.url_blacklist_re}")

        self._extractor = URLExtract(extract_localhost=False)

    def evaluate(self, text):
        trigger_urls = []
        trigger_entries = []

        if text and self.url_blacklist_re:  # searches for blacklisted (extracted) urls
            trigger_urls = list(filter(
                self.url_blacklist_re.match,
                self._extractor.find_urls(text, only_unique=True)
            ))

        if text and self.blacklist_re:  # searches for blacklisted text
            trigger_entries = re.findall(self.blacklist_re, text)

        logging.debug(f"Evaluated: {text}\n{trigger_urls}\n{trigger_entries}")
        return trigger_urls, trigger_entries
