import asyncio
import subprocess
from os import getcwd
from abc import ABC, abstractmethod
from discord_webhook import AsyncDiscordWebhook
from feedgen.feed import FeedGenerator
from pathlib import Path
from threading import Thread, Lock

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

class AtomFeedBuilder(Notifier):
    def __init__(self, feedId, title, authorName, feedLink, siteLink, logo, subtitle, language, path):
        fg = FeedGenerator()

        fg.id(feedId)
        fg.title(title)
        fg.author({'name':authorName})
        fg.link(href=feedLink, rel='self')
        fg.icon(logo)
        fg.subtitle(subtitle)
        fg.language(language)

        self.feedGenerator = fg
        self.feedPath = path

        # populate the feed with an initial dummy entry, since empty feeds are invalid
        fe = fg.add_entry()
        fe.id(f"{feedLink}/placeholder")
        fe.title("Placeholder Entry")
        fe.content("This feed is empty right now.")
        fe.link(href=siteLink)
        self.placeholderEntry = fe

        # make our dir if it doesn't exist already
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)

        fg.atom_file(path)

        self.mutex = Lock()

    def notify(self, title, content, *args, **kwargs):
        link = kwargs["link"];
        # use uuid param if provided, else fall back to post id
        entryId = kwargs.get('uuid', kwargs["post"]["_id"]);

        with self.mutex:
            fg = self.feedGenerator

            fe = fg.add_entry()
            fe.id(entryId)
            fe.title(title)
            fe.content(content)
            fe.link(href=link)

            # add/remove placeholder entry
            if (len(fg.entry()) == 0):
                fg.add_entry(self.placeholderEntry)
            elif (len(fg.entry()) > 1 and self.placeholderEntry in fg.entry()):
                fg.remove_entry(self.placeholderEntry)

            # only include a certain number of entries in the feed
            while (len(fg.entry()) > 10):
                fg.remove_entry(10)

            fg.atom_file(self.feedPath)

class DiscordNotifier(Notifier):
    def __init__(self, webhookUrl):
        self.url = webhookUrl
        self.event_loop = asyncio.new_event_loop()
        Thread(target=self.event_loop.run_forever).start()

    def notify(self, title, content, *args, **kwargs):
        link = kwargs["link"];

        webhook = AsyncDiscordWebhook(url=self.url, rate_limit_retry=True)
        webhook.content = f"[{title}](<{link}>)\n>>> {content}"
        asyncio.run_coroutine_threadsafe(webhook.execute(), self.event_loop)
