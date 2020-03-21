"""Contains all related to subjects."""
import logging
import os
from threading import Lock
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
from requests import Response

from _sha1 import sha1
from vcm.core.networking import Connection
from vcm.core.settings import DownloadSettings, GeneralSettings
from vcm.core.utils import secure_filename
from vcm.downloader.link import Chat, Kalvidres

from .alias import Alias
from .link import BaseLink, Delivery, Folder, ForumList, Resource


class Subject:
    """Representation of a subject."""

    def __init__(self, name, url, queue):
        """

        Args:
            name (str): name of the subject.
            url (str): url of the subject.
            queue (Queue): queue to controll threads.
        """

        name = name.capitalize().strip()

        self.name = Alias.id_to_alias(
            sha1(url.encode()).hexdigest(), GeneralSettings.root_folder / name
        ).name
        self.url = url
        self.connection = Connection()
        self.queue = queue

        self.enable_section_indexing = (
            self.url in DownloadSettings.section_indexing_urls
        )

        self.response: Response = None
        self.soup: BeautifulSoup = None
        self.notes_links = []
        self.folder_lock = Lock()
        self.hasfolder = False
        self.folder = GeneralSettings.root_folder / self.name
        self.logger = logging.getLogger(__name__)

        self.logger.debug(
            "Created %s(name=%r, url=%r)", type(self).__name__, self.name, self.url
        )

    def __repr__(self):
        return (
            f"{type(self).__name__}(name={self.name!r}, url={self.url!r}, "
            f"{len(self.notes_links)} notes links)"
        )

    def __str__(self):
        return f"{self.name}"

    def make_request(self):
        """Makes the primary request."""
        self.logger.debug("Making subject request")
        self.response = self.connection.get(self.url)
        self.soup = BeautifulSoup(self.response.text, "html.parser")

        self.logger.debug("Response obtained [%d]", self.response.status_code)
        self.logger.debug("Response parsed")

    def create_folder(self):
        """Creates the folder named as self."""
        if self.hasfolder is False:
            self.logger.debug("Creating folder %r", self.name)
            with self.folder_lock:
                if not self.folder.exists():
                    os.makedirs(self.folder.as_posix())
            self.hasfolder = True

        else:
            self.logger.debug("Folder already exists: %r", self.name)

    def add_link(self, link: BaseLink):
        """Adds a note link to the list."""
        self.logger.debug("Adding link: %s", link.name)
        if not self.enable_section_indexing:
            link.section = None

        self.notes_links.append(link)
        self.queue.put(link)

    @staticmethod
    def find_section_by_child(child):
        try:
            section_h3 = child.find_parent("li", class_="section main clearfix").find(
                "h3", class_="sectionname"
            )
        except AttributeError:
            section_h3 = child.find_parent(
                "li", class_="section main clearfix current"
            ).find("h3", class_="sectionname")
        return Section(section_h3.text, section_h3.a["href"])

    @staticmethod
    def url_to_query_args(url: str):
        return parse_qs(urlparse(url).query)

    def find_and_download_links(self):
        """Finds the links downloading the primary page."""
        self.logger.debug("Finding links of %s", self.name)
        self.make_request()

        _ = [x.extract() for x in self.soup.findAll("span", {"class": "accesshide"})]
        _ = [x.extract() for x in self.soup.findAll("div", {"class": "mod-indent"})]

        for folder in self.soup.find_all("div", class_="singlebutton"):
            folder_name = folder.parent.parent.div.find(
                "span", class_="fp-filename"
            ).text

            section = self.find_section_by_child(folder)

            folder_url = folder.form["action"]
            folder_icon_url = folder.find_parent(
                "div", class_="contentwithoutlink"
            ).find("img", class_="icon")["src"]
            id_ = folder.form.find("input", {"name": "id"})["value"]

            self.logger.debug(
                "Created Folder (subject search): %r, %s", folder_name, folder_url
            )
            self.add_link(
                Folder(folder_name, section, folder_url, folder_icon_url, self, id_)
            )

        for resource in self.soup.find_all("div", class_="activityinstance"):
            section = self.find_section_by_child(resource)

            name = resource.a.span.text
            url = resource.a["href"]
            icon_url = resource.a.img["src"]

            if "resource" in url:
                self.logger.debug(
                    "Created Resource (subject search): %r, %s", name, url
                )
                self.add_link(Resource(name, section, url, icon_url, self))
            elif "folder" in url:
                real_url = "https://campusvirtual.uva.es/mod/folder/download_folder.php"
                id_ = self.url_to_query_args(url)["id"][0]
                self.logger.debug(
                    "Created Folder (subject search): %r, id=%r", name, id_
                )
                self.add_link(Folder(name, section, real_url, icon_url, self, id_))
            elif "forum" in url:
                self.logger.debug("Created Forum (subject search): %r, %s", name, url)
                self.add_link(ForumList(name, section, url, icon_url, self))
            elif "chat" in url:
                self.logger.debug("Created Chat (subject search): %r, %s", name, url)
                self.add_link(Chat(name, section, url, icon_url, self))
            elif "assign" in url:
                self.logger.debug(
                    "Created Delivery (subject search): %r, %s", name, url
                )
                self.add_link(Delivery(name, section, url, icon_url, self))
            elif "kalvidres" in url:
                self.logger.debug(
                    "Created Kalvidres (subject search): %r, %s", name, url
                )
                self.add_link(Kalvidres(name, section, url, icon_url, self))

        self.logger.debug("Downloading files for subject %r", self.name)


class Section:
    def __init__(self, name, url=None):
        self.name = self.filter_name(name)
        self.url = url

        self.name = secure_filename(
            self.name, spaces=not DownloadSettings.secure_section_filename
        )

    def __str__(self):
        if self.url:
            return "Section(%r, url=%r)" % (self.name, self.url)
        return "Section(%r)" % self.name

    @staticmethod
    def filter_name(name):
        name = name.replace("\t", " ").strip()
        while "  " in name:
            name = name.replace("  ", " ")
        return name
