from enum import Enum, auto

from vcm.downloader.links import BaseLink
from vcm.notifier.database import DatabaseLinkInterface


class IconType(Enum):
    assign = auto()
    avi = auto()
    choice = auto()
    excel = auto()
    feedback = auto()
    folder = auto()
    forum = auto()
    jpeg = auto()
    mpeg = auto()
    page = auto()
    pdf = auto()
    powerpoint = auto()
    quiz = auto()
    sourcecode = auto()
    unkown = auto()
    url = auto()
    word = auto()
    workshop = auto()
    zip = auto()

    not_id = -1


URLS = {
    IconType.pdf: '1OBqjLDdO7newsN8gtLkUEc61kIVsCCI2',
    IconType.zip: '1S4lRY6iDw8uqelEkOiEdTS5kiJJPdsjV',
    IconType.word: '1VeGEeGyDZ7VTYhzXtb_k068urpeyie7-',
    IconType.forum: '1ChuqxOgaSkOHNrABtWEulazaQt4gG6J_',
    IconType.page: '1c9UZxb0vqP7QtgMdit_YqO5rdIe6oLNV',
    IconType.url: '1LPTP1oKhtXvGu3oApLBXdqHZmkJK81el',
    IconType.assign: '1l056BB9rIuvC_2DsClt81i2VsGtPLAqN',
    IconType.feedback: '1uZLx-knwrtI1gwL44ehvLs2wOmsO5Isd',
    IconType.quiz: '1Wfr3ube0J8ZAn5sHSjMtzNLatFTJmT6k',
    IconType.unkown: '12BL-MLAEv5gEd2HqusEUE7ohR1kIZdLa',
    IconType.choice: '10KReH-TLyBPMcerOQ4J7nZ-ARzYHYIet',
    IconType.folder: '1QBcHalK6zRx_MX7H6_zDRuuJjte9dBMj',
    IconType.workshop: '12yclWnyEiQpyuRR4cRJAGyMJHrcJabpz',
    IconType.avi: '1Hd3sAjz6BX6RfOBg3X5E2VZ603KsMyZj',
    IconType.mpeg: '1BpafvF0WBvGCjLCjUruBtyzAIDkgWOXx',
    IconType.sourcecode: '1LOYPh2Z1YWlAX6kRuYdiYY_-QsOEfuEh',
    IconType.excel: '12THl4cPW2phdmiQ9mHAKGg_6PP_ym8iS',
    IconType.powerpoint: '1uXo1sjW24dDokCF2u7ek_Ylq_YBezvab',
    IconType.jpeg: '1tXp7K0uv5vGxsPeudKcGxTr0q-I2GdJs',
}

for key in URLS.keys():
    URLS[key] = 'https://drive.google.com/uc?export=download&id=' + URLS[key]


class NotifierLink(BaseLink):
    def __init__(self, name, url, icon_url, subject, connection, queue):
        super().__init__(name, url, icon_url, subject, connection, queue)
        self._icon_type = None

    @classmethod
    def from_link(cls, link: BaseLink):
        dir_notifier_link = ['name', 'url', 'icon_url', 'subject', 'connection', 'queue']
        new_vars = {}

        for attribute in dir_notifier_link:
            try:
                new_vars[attribute] = getattr(link, attribute)
            except AttributeError:
                pass

        new_vars['icon_url'] = getattr(link, '_icon_url')
        return NotifierLink(**new_vars)

    def save(self):
        return DatabaseLinkInterface.save(self)

    def gen_icon_type(self):
        return self.icon_type

    @property
    def icon_type(self):
        if self._icon_type:
            return self._icon_type

        if 'pdf' in self._icon_url:
            self._icon_type = IconType.pdf
        elif 'archive' in self._icon_url:
            self._icon_type = IconType.zip
        elif '/forum' in self._icon_url:
            self._icon_type = IconType.forum
        elif '/page' in self._icon_url:
            self._icon_type = IconType.page
        elif '/url' in self._icon_url:
            self._icon_type = IconType.url
        elif '/assign' in self._icon_url:
            self._icon_type = IconType.assign
        elif '/feedback' in self._icon_url:
            self._icon_type = IconType.feedback
        elif '/quiz' in self._icon_url:
            self._icon_type = IconType.quiz
        elif '/choice' in self._icon_url:
            self._icon_type = IconType.choice
        elif '/folder' in self._icon_url:
            self._icon_type = IconType.folder
        elif '/workshop' in self._icon_url:
            self._icon_type = IconType.workshop

        elif '/f/unknown' in self._icon_url:
            self._icon_type = IconType.unkown
        elif '/f/document' in self._icon_url:
            self._icon_type = IconType.word
        elif '/f/mpeg' in self._icon_url:
            self._icon_type = IconType.mpeg
        elif '/f/avi' in self._icon_url:
            self._icon_type = IconType.avi
        elif '/f/sourcecode' in self._icon_url:
            self._icon_type = IconType.sourcecode
        elif '/f/spreadsheet' in self._icon_url:
            self._icon_type = IconType.excel
        elif '/f/powerpoint' in self._icon_url:
            self._icon_type = IconType.powerpoint
        elif '/f/jpeg' in self._icon_url:
            self._icon_type = IconType.jpeg
        else:
            self._icon_type = IconType.not_id

        return self._icon_type

    @property
    def icon_url(self):
        try:
            return URLS[self.icon_type]
        except KeyError:
            return 'https://invalid.invalid.es'

    def __repr__(self):
        return f'Link({self.subject!r}, {self.name!r})'
