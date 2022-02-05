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

        #open link when clicking on notification
        if 'link' in kwargs:
            args = args + ['--action', f'termux-open-url {kwargs["link"]}']

        #add buttons to the notification
        if 'buttons' in kwargs:
            post = kwargs["post"]
            for i, button in enumerate(kwargs["buttons"], start=1):
                args = args + [f'--button{i}', button["text"],
                    f'--button{i}-action', f'python3 {getcwd()}/notification_button.py -b {post["board"]} -p {post["postId"]} -a {button["actions"]}']

        subprocess.call(args)

class NotifySendNotifier(Notifier):
    def notify(self, title, content, *args, **kwargs):
        subprocess.call(['notify-send', title, content])
