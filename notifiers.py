import subprocess
from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def notify(self, title, content, *args, **kwargs):
        raise NotImplementedError


class TermuxNotifier(Notifier):
    def notify(self, title, content, *args, **kwargs):
        subprocess.call(['termux-notification', '--title', title, '--content', content])


class NotifySendNotifier(Notifier):
    def notify(self, title, content, *args, **kwargs):
        subprocess.call(['notify-send', title, content])
