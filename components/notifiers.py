import subprocess
from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def notify(self, title, content, url, *args, **kwargs):
        raise NotImplementedError


class TermuxNotifier(Notifier):
    def notify(self, title, content, url, *args, **kwargs):
        print(url)
        subprocess.call(['termux-notification', '--title', title, '--content', content or 'No Message', '--action', 'termux-open-url', url])


class NotifySendNotifier(Notifier):
    def notify(self, title, content, url, *args, **kwargs):
        print(url)
        subprocess.call(['notify-send', title, content])
