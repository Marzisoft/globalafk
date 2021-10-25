import logging
import re

from urlextract import URLExtract

from config import config


def _format_match(match):
    s, e = match.start(0), match.end(0)
    m = match.string[:s] + config.TRIGGER_WRAPPER + match.string[s:e] + config.TRIGGER_WRAPPER + match.string[e:]
    return m[s - config.TRIGGER_OFFSET or 0:e if e + config.TRIGGER_OFFSET > len(m) else e + config.TRIGGER_OFFSET]


class Evaluator:
    def __init__(self):

        if config.TRIGGER_ON_BLACKLISTED:
            self.blacklist_re = re.compile('|'.join(config.BLACKLIST), re.IGNORECASE)
            logging.debug(f'Compiled blacklist: {self.blacklist_re}')

        if config.TRIGGER_ON_NON_WHITELISTED_URLS:
            self.url_blacklist_re = re.compile(f'(?!{"|".join(config.URL_WHITELIST)})', re.IGNORECASE)
            self._url_extractor = URLExtract(extract_localhost=False)
            logging.debug(f'Compiled url blacklist:{self.url_blacklist_re}')

    def evaluate(self, text):
        trigger_urls = [
            *filter(self.url_blacklist_re.match, self._url_extractor.find_urls(text, only_unique=True))
        ] if config.TRIGGER_ON_NON_WHITELISTED_URLS and text else []
        trigger_entries = [
            _format_match(entry) for entry in re.finditer(self.blacklist_re, text)
        ] if config.TRIGGER_ON_BLACKLISTED and text else []

        logging.debug(f'Evaluated: {text}\n{trigger_urls or []}\n{trigger_entries}')
        return trigger_urls, trigger_entries
