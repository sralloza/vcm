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
        elif '/forum/1566977852/icon' in self._icon_url:
            self._icon_type = IconType.forum
        elif '/page/1535396818/icon' in self._icon_url:
            self._icon_type = IconType.page
        elif '/url/1535396818/icon' in self._icon_url:
            self._icon_type = IconType.url
        elif '/assign/1566977852/icon' in self._icon_url:
            self._icon_type = IconType.assign
        elif '/feedback/1535396818/icon' in self._icon_url:
            self._icon_type = IconType.feedback
        elif '/quiz/1535396818/icon' in self._icon_url:
            self._icon_type = IconType.quiz
        elif '/choice/1535396818/icon' in self._icon_url:
            self._icon_type = IconType.choice
        elif '/folder/1535396818/icon' in self._icon_url:
            self._icon_type = IconType.folder
        elif '/workshop/1535396818/icon' in self._icon_url:
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
        icon_type = self.icon_type
        if icon_type == IconType.pdf:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1OBqjLDdO7newsN8gtLkUEc61kIVsCCI2'
        if icon_type == IconType.zip:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1S4lRY6iDw8uqelEkOiEdTS5kiJJPdsjV'
        if icon_type == IconType.word:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1VeGEeGyDZ7VTYhzXtb_k068urpeyie7-'
        if icon_type == IconType.forum:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1ChuqxOgaSkOHNrABtWEulazaQt4gG6J_'
        if icon_type == IconType.page:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1c9UZxb0vqP7QtgMdit_YqO5rdIe6oLNV'
        if icon_type == IconType.url:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1LPTP1oKhtXvGu3oApLBXdqHZmkJK81el'
        if icon_type == IconType.assign:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1l056BB9rIuvC_2DsClt81i2VsGtPLAqN'
        if icon_type == IconType.feedback:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1uZLx-knwrtI1gwL44ehvLs2wOmsO5Isd'
        if icon_type == IconType.quiz:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1Wfr3ube0J8ZAn5sHSjMtzNLatFTJmT6k'
        if icon_type == IconType.unkown:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=12BL-MLAEv5gEd2HqusEUE7ohR1kIZdLa'
        if icon_type == IconType.choice:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=10KReH-TLyBPMcerOQ4J7nZ-ARzYHYIet'
        if icon_type == IconType.folder:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1QBcHalK6zRx_MX7H6_zDRuuJjte9dBMj'
        if icon_type == IconType.workshop:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=12yclWnyEiQpyuRR4cRJAGyMJHrcJabpz'
        if icon_type == IconType.avi:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1Hd3sAjz6BX6RfOBg3X5E2VZ603KsMyZj'
        if icon_type == IconType.mpeg:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1BpafvF0WBvGCjLCjUruBtyzAIDkgWOXx'
        if icon_type == IconType.sourcecode:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1LOYPh2Z1YWlAX6kRuYdiYY_-QsOEfuEh'
        if icon_type == IconType.excel:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=12THl4cPW2phdmiQ9mHAKGg_6PP_ym8iS'
        if icon_type == IconType.powerpoint:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1uXo1sjW24dDokCF2u7ek_Ylq_YBezvab'
        if icon_type == IconType.jpeg:
            return 'https://drive.google.com/uc?export=download&' \
                   'id=1tXp7K0uv5vGxsPeudKcGxTr0q-I2GdJs'

        return 'https://invalid.invalid.es'

    def __repr__(self):
        return f'Link({self.subject!r}, {self.name!r})'
