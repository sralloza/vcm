import json
from enum import Enum, auto
from pathlib import Path

from vcm.downloader.link import BaseLink, Folder
from vcm.notifier.database import DatabaseLinkInterface

inline_style = "border: none; outline: none; background: none; cursor: pointer; color: #0000EE; padding: 0; text-decoration: underline; font-family: inherit; font-size: inherit;"


class IconType(Enum):
    assign = auto()
    avi = auto()
    chat = auto()
    choice = auto()
    excel = auto()
    feedback = auto()
    folder = auto()
    forum = auto()
    jpeg = auto()
    kalvidres = auto()
    mpeg = auto()
    page = auto()
    pdf = auto()
    powerpoint = auto()
    quiz = auto()
    sourcecode = auto()
    unknown = auto()
    url = auto()
    word = auto()
    workshop = auto()
    zip = auto()



ICON_URLS = {
    IconType.assign: "1PRXBCb3DfAIUqLtq1MgtbkfQVrEd53rn",
    IconType.avi: "1lK5PPQXOye3JF8_KMo-6597HykOHWIWt",
    IconType.chat: "14HuXDc42lIS5xENXTnqwzsJUppZZHB7E",
    IconType.choice: "1RRwJb2xEZjrthl3-KvMqLpYqQeY3jfDJ",
    IconType.excel: "1OiJq2MDfE-OlRLLe8A1piBxEZLuWkZaN",
    IconType.feedback: "1R1HwfJJCt5QHGIsq9BVI1aVQO0_MYD_7",
    IconType.folder: "1uPJPWNafdsKDiSTVj76N-IVfHO4UjiuX",
    IconType.forum: "1oQ0RfIXqW-Y5H3h46c5VAygDUpQuWUn5",
    IconType.jpeg: "1_Q9H2qMNHESPPvCQhhEMPTH9-kPiwrhP",
    IconType.kalvidres: "1j6v7D2DK7IP2iumxAcsHiMLEN90AbMsq",
    IconType.mpeg: "1-Hvsx0JMCvLp-cBJmAAJYpl_stj468NM",
    IconType.page: "1TH8Ljf5RFfG54Lg4HVGLnQDe2wWmH9Y-",
    IconType.pdf: "1AXdOsygBu0KMHKbrhD3bY73KrKb6eHuD",
    IconType.powerpoint: "1lBaoEmG9sz2-0Wu-WznKWm3WYoAyzSCC",
    IconType.quiz: "1qyFrM5VrQWUVIMU3hSnkBa2th-04cH8t",
    IconType.sourcecode: "1mBb_cSq5sCSxfAo6M9xx8QbIHUlOgFvz",
    IconType.unknown: "1mBb_cSq5sCSxfAo6M9xx8QbIHUlOgFvz",
    IconType.url: "1ikffKbgEuP8HrU1AJ9HL0VEWswLH2v1g",
    IconType.word: "1Dce2TCwcYVfwrq43CMNbdTtUb3kjIUft",
    IconType.workshop: "1CacYmQs-YYC-uce7HyPWWdemWi5uq3hd",
    IconType.zip: "1zU7SfEx-DI5GpVJAJ3MN7isu9t48inAL",
}

TEMPLATE = "https://drive.google.com/uc?export=download&id=%s"
ICON_URLS = {x: TEMPLATE % ICON_URLS[x] for x in ICON_URLS}

class NotifierLink(BaseLink):
    def __init__(
        self,
        name,
        section,
        url,
        icon_url,
        subject,
        parent=None,
        super_class=None,
        id=None,
    ):
        super().__init__(name, section, url, icon_url, subject, parent)
        self._icon_type = None
        self.super_class = super_class
        self.id = id

    @classmethod
    def from_link(cls, link: BaseLink):
        dir_notifier_link = [
            "name",
            "section",
            "url",
            "icon_url",
            "subject",
            "parent",
            "icon_url",
        ]
        new_vars = {}

        for attribute in dir_notifier_link:
            try:
                new_vars[attribute] = getattr(link, attribute)
            except AttributeError:
                pass

        try:
            new_vars["id"] = link.id
        except AttributeError:
            pass

        new_vars["super_class"] = link.__class__

        return NotifierLink(**new_vars)

    def save(self):
        return DatabaseLinkInterface.save(self)

    def delete(self):
        return DatabaseLinkInterface.delete(self)

    def gen_icon_type(self):
        return self.icon_type

    @property
    def icon_type(self):
        if self._icon_type:
            return self._icon_type

        if "pdf" in self.icon_url:
            self._icon_type = IconType.pdf
        elif "archive" in self.icon_url:
            self._icon_type = IconType.zip
        elif "/forum" in self.icon_url:
            self._icon_type = IconType.forum
        elif "/chat" in self.icon_url:
            self._icon_type = IconType.chat
        elif "/page" in self.icon_url:
            self._icon_type = IconType.page
        elif "/url" in self.icon_url:
            self._icon_type = IconType.url
        elif "/assign" in self.icon_url:
            self._icon_type = IconType.assign
        elif "/feedback" in self.icon_url:
            self._icon_type = IconType.feedback
        elif "/quiz" in self.icon_url:
            self._icon_type = IconType.quiz
        elif "/choice" in self.icon_url:
            self._icon_type = IconType.choice
        elif "/folder" in self.icon_url:
            self._icon_type = IconType.folder
        elif "/workshop" in self.icon_url:
            self._icon_type = IconType.workshop
        elif "/kalvidres" in self.icon_url:
            self._icon_type = IconType.kalvidres
        elif "/f/unknown" in self.icon_url:
            self._icon_type = IconType.unknown
        elif "/f/document" in self.icon_url:
            self._icon_type = IconType.word
        elif "/f/mpeg" in self.icon_url:
            self._icon_type = IconType.mpeg
        elif "/f/avi" in self.icon_url:
            self._icon_type = IconType.avi
        elif "/f/sourcecode" in self.icon_url:
            self._icon_type = IconType.sourcecode
        elif "/f/spreadsheet" in self.icon_url:
            self._icon_type = IconType.excel
        elif "/f/powerpoint" in self.icon_url:
            self._icon_type = IconType.powerpoint
        elif "/f/jpeg" in self.icon_url:
            self._icon_type = IconType.jpeg
        else:
            self._icon_type = IconType.unknown

        return self._icon_type

    @property
    def generated_icon_url(self):
        try:
            return ICON_URLS[self.icon_type]
        except KeyError:
            return str(self.icon_type)

    def __repr__(self):
        return f"Link({self.subject!r}, {self.name!r})"

    def to_html(self):
        if self.super_class != Folder:
            return f'<a href="{self.url}">{self.name}</a>'

        return f"""
        <form action="{self.url}" method="POST" style="display: inline;">
            <input name="id" type="hidden" value="{self.id}">
            <input type="submit" style="{inline_style}" value="{self.name}">
        </form>
        """
