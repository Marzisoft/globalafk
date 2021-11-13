import logging
import re
from abc import ABC, abstractmethod

from urlextract import URLExtract


class Evaluator(ABC):
    @abstractmethod
    def eval(self, text, *args, **kwargs):
        raise NotImplementedError


class PostEvaluator(Evaluator):
    def __init__(self, blacklist=(), url_whitelist=()):
        self.blacklist_re = re.compile('|'.join(blacklist), re.IGNORECASE) if blacklist else None
        if url_whitelist:
            self.url_blacklist_re = re.compile(f'(?!{"|".join(url_whitelist)})', re.IGNORECASE)
            self._url_extractor = URLExtract(extract_localhost=False)
        else:
            self.url_blacklist_re = None
        logging.debug(f'Compiled regex\nblacklist:{self.blacklist_re}\nurl blacklist:{self.url_blacklist_re}')

    def eval(self, text, *args, **kwargs):
        trigger_urls = [
            *filter(self.url_blacklist_re.match, self._url_extractor.find_urls(text, only_unique=True))
        ] if self.url_blacklist_re and text else []
        trigger_entries = [
            _format_match(entry) for entry in re.finditer(self.blacklist_re, text)
        ] if self.blacklist_re and text else []
        logging.debug(f'Evaluated text:{text}\ntrigger urls:{trigger_urls}\ntrigger entries:{trigger_entries}')
        return trigger_urls, trigger_entries
