"""Contains all related to subjects."""

import logging
import os
from threading import Lock

from bs4 import BeautifulSoup
from requests import Response

from _sha1 import sha1
from vcm.core.networking import Connection
from vcm.core.settings import GeneralSettings

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

        self.name = Alias.real_to_alias(sha1(url.encode()).hexdigest(), name)
        self.url = url
        self.connection = Connection()
        self.queue = queue

        self.response: Response = None
        self.soup: BeautifulSoup = None
        self.notes_links = []
        self.folder_lock = Lock()
        self.hasfolder = False
        # self.folder = GeneralSettings.root_folder / secure_filename(self.name)
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

    def add_link(self, url: BaseLink):
        """Adds a note url to the list."""
        self.logger.debug("Adding url: %s", url.name)
        self.notes_links.append(url)
        self.queue.put(url)

    def find_and_download_links(self):
        """Finds the links downloading the primary page."""
        self.logger.debug("Finding links of %s", self.name)
        self.make_request()

        _ = [x.extract() for x in self.soup.findAll("span", {"class": "accesshide"})]
        _ = [x.extract() for x in self.soup.findAll("div", {"class": "mod-indent"})]

        search = self.soup.findAll("li", class_="activity")

        for li in search:
            try:
                div = li.find("div", class_="activityinstance")
                id_ = None

                if not div:  # Folder
                    div = li.find("div", class_="singlebutton")
                    name = li.find("span", class_="fp-filename").text
                    url = div.form["action"]
                    id_ = div.find("input", {"name": "id"})["value"]
                    icon_url = li.find("span", class_="fp-icon").img["src"]
                else:
                    name = div.a.span.text
                    url = div.a["href"]
                    icon_url = div.a.img["src"]

                if "resource" in url:
                    self.logger.debug(
                        "Created Resource (subject search): %r, %s", name, url
                    )
                    self.add_link(Resource(name, section_name, url, icon_url, self))
                elif "folder" in url:
                    self.logger.debug(
                        "Created Folder (subject search): %r, %s", name, url
                    )
                    self.add_link(Folder(name, section_name, url, icon_url, self, id_))
                elif "forum" in url:
                    self.logger.debug(
                        "Created Forum (subject search): %r, %s", name, url
                    )
                    self.add_link(ForumList(name, section_name, url, icon_url, self))
                elif "assign" in url:
                    self.logger.debug(
                        "Created Delivery (subject search): %r, %s", name, url
                    )

            except AttributeError:
                pass
                    self.add_link(Delivery(name, section_name, url, icon_url, self))

        self.logger.debug("Downloading files for subject %r", self.name)
