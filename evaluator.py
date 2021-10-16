import logging
import re

from urlextract import URLExtract

from config import config


class Evaluator:
    def __init__(self):
        self.blacklist_re = re.compile('|'.join(config.BLACKLIST), re.IGNORECASE)
        self.url_blacklist_re = re.compile(f'(?!{"|".join(config.URL_WHITELIST)})', re.IGNORECASE)

        logging.debug(f'Compiled, url blacklist regex: {self.url_blacklist_re}\n blacklist regex: {self.blacklist_re}')

        self.__extractor = URLExtract(extract_localhost=False)

    def evaluate(self, text):
        if not text:
            return [], []

        trigger_urls = [*filter(self.url_blacklist_re.match, self.__extractor.find_urls(text, only_unique=True))]
        trigger_entries = [entry.group(0) for entry in re.finditer(self.blacklist_re, text)]

        logging.debug(f'Evaluated: {text}\n{trigger_urls}\n{trigger_entries}')

        return trigger_urls, trigger_entries
