import subprocess
from os import getcwd
from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def notify(self, title, content, *args, **kwargs):
        raise NotImplementedError

class TermuxNotifier(Notifier):
    def notify(self, title, content, *args, **kwargs):
        args = ['termux-notification', '--title', title,
            '--content', content or 'No Message']
        if 'url' in kwargs:
            args = args + ['--action', f'termux-open-url {kwargs["url"]}',
                '--button1', 'Delete',
                '--button1-action', f'python3 {getcwd()}/notification_button.py -b {kwargs["board"]} -p {kwargs["postId"]} -a delete',
                '--button2', 'Delete+Ban',
                '--button2-action', f'python3 {getcwd()}/notification_button.py -b {kwargs["board"]} -p {kwargs["postId"]} -a delete,ban',
                '--button3', 'Delete+Global Ban',
                '--button3-action', f'python3 {getcwd()}/notification_button.py -b {kwargs["board"]} -p {kwargs["postId"]} -a delete,global_ban']
        subprocess.call(args)

class NotifySendNotifier(Notifier):
    def notify(self, title, content, *args, **kwargs):
        subprocess.call(['notify-send', title, content])
