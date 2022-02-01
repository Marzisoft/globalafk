import subprocess
from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def notify(self, title, content, *args, **kwargs):
        raise NotImplementedError


class TermuxNotifier(Notifier):
    def notify(self, title, content, *args, **kwargs):
        subprocess.call(['termux-notification', '--title', title,
            '--content', content or 'No Message',
            '--action', f'termux-open-url {kwargs["url"]}'
            '--button1', 'Delete',
            '--button1-action', f'python3 notification_button.py -b {kwargs["board"]} -p {kwargs["postId"]} -a delete',
            '--button2', 'Ban+Delete',
            '--button2-action', f'python3 notificaiton_button.py -b {kwargs["board"]} -p {kwargs["postId"]} -a delete+ban',
            '--button3', 'Dismiss',
            '--button3-action', f'python3 notification_button.py -b {kwargs["board"]} -p {kwargs["postId"]} -a dismiss'])

class NotifySendNotifier(Notifier):
    def notify(self, title, content, *args, **kwargs):
        subprocess.call(['notify-send', title, content])
