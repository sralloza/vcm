import json
from enum import Enum, auto
from pathlib import Path

from vcm.downloader.link import BaseLink, Folder
from vcm.notifier.database import DatabaseLinkInterface

inline_style = "border: none; outline: none; background: none; cursor: pointer; color: #0000EE; padding: 0; text-decoration: underline; font-family: inherit; font-size: inherit;"


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
    unknown = auto()
    url = auto()
    word = auto()
    workshop = auto()
    zip = auto()


base64path = Path(__file__).parent / "base64.json"

with base64path.open() as f:
    data = json.load(f)

IMAGE_DATA = {icon_type: data[icon_type.name] for icon_type in IconType}
del data

URLS = {
    IconType.assign: "https://campusvirtual.uva.es/theme/image.php/uva2017/assign/1577957563/icon",
    IconType.avi: "https://campusvirtual.uva.es/theme/image.php/uva2017/core/1566299165/f/avi-24",
    IconType.choice: "https://campusvirtual.uva.es/theme/image.php/uva2017/choice/1566299165/icon",
    IconType.excel: "https://campusvirtual.uva.es/theme/image.php/uva2017/core/1577957563/f/spreadsheet-24",
    IconType.feedback: "https://campusvirtual.uva.es/theme/image.php/uva2017/feedback/1566299165/icon",
    IconType.folder: "https://campusvirtual.uva.es/theme/image.php/uva2017/folder/1577957563/icon",
    IconType.forum: "https://campusvirtual.uva.es/theme/image.php/uva2017/forum/1577957563/icon",
    IconType.jpeg: "https://campusvirtual.uva.es/theme/image.php/uva2017/core/1566299165/f/jpeg-24",
    IconType.mpeg: "https://campusvirtual.uva.es/theme/image.php/uva2017/core/1566299165/f/mpeg-24",
    IconType.page: "https://campusvirtual.uva.es/theme/image.php/uva2017/page/1577957563/icon",
    IconType.pdf: "https://campusvirtual.uva.es/theme/image.php/uva2017/core/1577957563/f/pdf-24",
    IconType.powerpoint: "https://campusvirtual.uva.es/theme/image.php/uva2017/core/1577957563/f/powerpoint-24",
    IconType.quiz: "https://campusvirtual.uva.es/theme/image.php/uva2017/quiz/1577957563/icon",
    IconType.sourcecode: IconType.unknown,
    IconType.unknown: "https://campusvirtual.uva.es/theme/image.php/uva2017/core/1577957563/f/html-24",
    IconType.url: "https://campusvirtual.uva.es/theme/image.php/uva2017/url/1577957563/icon",
    IconType.word: "https://campusvirtual.uva.es/theme/image.php/uva2017/core/1577957563/f/document-24",
    IconType.workshop: "https://campusvirtual.uva.es/theme/image.php/uva2017/workshop/1566299165/icon",
    IconType.zip: "https://campusvirtual.uva.es/theme/image.php/uva2017/core/1577957563/f/archive-24",
}


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
            return URLS[self.icon_type]
        except KeyError:
            return str(self.icon_type)

    @property
    def icon_data_64(self):
        return IMAGE_DATA[self.icon_type]

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
