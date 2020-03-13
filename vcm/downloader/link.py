"""Contains the links that can be downloaded."""
import logging
import os
import random
import warnings
from pathlib import Path

import unidecode
from bs4 import BeautifulSoup
from requests import Response

from hashlib import sha1
from vcm.core.modules import Modules
from vcm.core.results import Results
from vcm.core.settings import GeneralSettings
from vcm.core.utils import Patterns, secure_filename
from vcm.core.networking import Connection

from .alias import Alias
from .filecache import REAL_FILE_CACHE


class _Notify:
    NOTIFY = False

    @property
    def notify(self):
        return self.NOTIFY


class BaseLink(_Notify):
    """Base class for Links."""

    def __init__(self, name, section, url, icon_url, subject, parent=None):
        """
        Args:
            name (str): name of the url.
            url (str): URL of the url.
            icon_url (str or None): URL of the icon.
            subject (vcm.subject.Subject): subject of the url.
            parent (BaseLink): object that created self.
        """

        self.name = name.strip()
        self.section = section
        self.url = url
        self.icon_url = icon_url
        self.subject = subject
        self.connection = Connection()
        self.parent = parent

        self.response: Response = None
        self.soup: BeautifulSoup = None
        self.filepath: Path = None
        self.redirect_url = None
        self.response_name = None
        self.subfolders = []

        self.logger = logging.getLogger(__name__)
        self.logger.debug(
            "Created %s(name=%r, url=%r, subject=%r)",
            self.__class__.__name__,
            self.name,
            self.url,
            self.subject.name,
        )

    @property
    def content_disposition(self):
        if self.response is None:
            raise RuntimeError("Response not made yet")

        return unidecode.unidecode(self.response.headers["Content-Disposition"])

    def append_subfolder(self, dirname):
        dirname = secure_filename(dirname)
        return self.subfolders.append(dirname)

    def insert_subfolder(self, index, dirname):
        dirname = secure_filename(dirname)
        return self.subfolders.insert(index, dirname)

    def create_subfolder(self):
        """Creates the subfolder, if it is configured."""
        self.create_subject_folder()

        if not self.filepath:
            self.autoset_filepath()

        folder: Path = self.filepath.parent

        if not folder.exists():
            os.makedirs(folder.as_posix(), exist_ok=True)
            self.logger.debug("Created subfolder %r", folder.as_posix())
        else:
            self.logger.debug("Subfolder already exists %r", folder.as_posix())

    @staticmethod
    def _process_filename(filepath: str):
        """Quits some characters from the filename that can not be in a filepath.

        Args:
            filepath (st): filepath to process.

        Returns:
            str: filepath processed.

        """

        filepath = filepath.replace(">", " mayor que ")
        filepath = filepath.replace("<", " menor que ")

        return filepath

    @staticmethod
    def _filename_to_ext(filename):
        """Returns the extension given a filename."""
        return Path(filename).suffix[1:]

    def _get_ext_from_response(self):
        """Returns the extension of the filename of the response, got from the Content-Dispotition
        HTTP header.

        Returns:
            str: the extension.

        """

        if self.response_name is not None:
            return self._filename_to_ext(self.response_name)

        try:
            # unidecode.unidecode is used to remove accents.
            self.response_name = Patterns.FILENAME_PATTERN.search(
                self.content_disposition
            ).group(1)
            return self._filename_to_ext(self.response_name)
        except KeyError:
            pass

        self.response_name = Path(self.url).name
        return self._filename_to_ext(self.response_name) or "ukn"

    def create_subject_folder(self):
        """Creates the subject's principal folder."""
        return self.subject.create_folder()

    def make_request(self):
        """Makes the request for the Link."""

        self.logger.debug("Making request")

        self.response = self.connection.get(
            self.redirect_url or self.url, timeout=GeneralSettings.timeout
        )

        self.logger.debug("Response obtained [%d]", self.response.status_code)

        if self.response.status_code == 408:
            self.logger.warning("Received response with code 408, retrying")
            return self.make_request()

    def close_connection(self):
        warnings.warn(
            "Since streams are not used, this method should not be called",
            DeprecationWarning,
        )
        self.logger.debug("Closing connection")
        self.response.close()

    def process_request_bs4(self):
        """Parses the response with BeautifulSoup with the html parser."""

        self.logger.debug("Parsing response (bs4)")
        self.soup = BeautifulSoup(self.response.text, "html.parser")
        self.logger.debug("Response parsed (bs4)")

    def autoset_filepath(self):
        """Determines the filepath of the Link."""

        if self.filepath is not None:
            self.logger.debug("Filepath is setted, skipping (%s)", self.filepath)
            return

        if self.response is None:
            raise RuntimeError("Request not launched")

        filename = secure_filename(
            self._process_filename(self.name) + "." + self._get_ext_from_response()
        )

        temp_filepath = self.subject.folder

        if self.subfolders:
            temp_filepath.joinpath(*self.subfolders)

        if self.section:
            temp_filepath /= self.section.name

        temp_filepath /= filename

        try:
            folder_id = self.id
        except AttributeError:
            folder_id = None

        self.filepath = Path(
            Alias.id_to_alias(
                sha1(self.url.encode()).hexdigest(),
                temp_filepath.as_posix(),
                folder_id,
            )
        )

        self.logger.debug("Set filepath: %r", self.filepath)

    def download(self):
        """Abstract method to download the Link. Must be overridden by subclasses."""
        self.logger.debug("Called download() but it was not implemented")
        raise NotImplementedError

    def get_header_length(self):
        try:
            return int(self.response.headers["Content-Length"])
        except KeyError:
            return len(self.response.content)

    @property
    def content_type(self):
        if "Content-Type" in self.response.headers:
            return self.response.headers["Content-Type"]

        return None

    def save_response_content(self):
        """Saves the response content to the disk."""
        if self.filepath is None:
            self.autoset_filepath()

        if Modules.current() == Modules.notify:
            return

        self.create_subfolder()

        self.logger.debug(
            "filepath in REAL_FILE_CACHE: %s", self.filepath in REAL_FILE_CACHE
        )

        if self.filepath in REAL_FILE_CACHE:
            if REAL_FILE_CACHE[self.filepath] == self.get_header_length():
                self.logger.debug(
                    "File found in cache: Same content (%d)", len(self.response.content)
                )
                return

            self.logger.debug(
                "File found in cache: Different content (%d --> %d)",
                REAL_FILE_CACHE[self.filepath],
                len(self.response.content),
            )
            Results.print_updated(self.filepath)
        else:
            self.logger.debug(
                "File added to cache: %s [%d]",
                self.filepath,
                len(self.response.content),
            )
            REAL_FILE_CACHE[self.filepath] = len(self.response.content)
            Results.print_new(self.filepath)

        try:
            with self.filepath.open("wb") as file_handler:
                file_handler.write(self.response.content)
            self.logger.debug("File downloaded and saved: %s", self.filepath)
        except PermissionError:
            self.logger.warning(
                "File couldn't be downloaded due to permission error: %s",
                self.filepath.name,
            )
            self.logger.warning(
                "Permission error %s -- %s", self.subject.name, self.filepath.name
            )

    @staticmethod
    def ensure_origin(url: str) -> bool:
        """Returns True if the origin is the virtual campus."""
        return "campusvirtual.uva.es" in url


class Resource(BaseLink):
    """Representation of a resource."""

    NOTIFY = True

    def __init__(self, name, section, url, icon_url, subject, parent=None):
        super().__init__(name, section, url, icon_url, subject, parent)
        self.resource_type = "unknown"

    def set_resource_type(self, new):
        """Sets a new resource type.

        Args:
            new (str): new resource type.
        """
        self.logger.debug("Set resource type: %r", new)
        self.resource_type = new

        if self.resource_type == "html":
            self.process_request_bs4()

    def download(self):
        """Downloads the resource."""
        self.logger.debug("Downloading resource %s", self.name)

        url = self.redirect_url or self.url
        if not self.ensure_origin(url):
            self.logger.warning(
                "Permision denied: URL is outside of campusvirtual.uva.es"
            )
            return

        self.make_request()

        if self.response.status_code == 404:
            self.logger.error("state code of 404 in url %r [%r]", self.url, self.name)
            return None

        if "application/pdf" in self.content_type:
            self.set_resource_type("pdf")
            return self.save_response_content()

        if "officedocument.wordprocessingml.document" in self.content_type:
            self.set_resource_type("word")
            return self.save_response_content()

        if "officedocument.spreadsheetml.sheet" in self.content_type or "excel" in self.content_type:
            self.set_resource_type("excel")
            return self.save_response_content()

        if "officedocument.presentationml.slideshow" in self.content_type:
            self.set_resource_type("power-point")
            return self.save_response_content()

        if "presentationml.presentation" in self.content_type:
            self.set_resource_type("power-point")
            return self.save_response_content()

        if "powerpoint" in self.content_type:
            self.set_resource_type("power-point")
            return self.save_response_content()

        if "msword" in self.content_type:
            self.set_resource_type("word")
            return self.save_response_content()

        if "application/zip" in self.content_type:
            self.set_resource_type("zip")
            return self.save_response_content()

        if "application/g-zip" in self.content_type:
            self.set_resource_type("gzip")
            return self.save_response_content()

        if "application/x-7z-compressed" in self.content_type:
            self.set_resource_type("7zip")
            return self.save_response_content()

        if "x-rar-compressed" in self.content_type:
            self.set_resource_type("rar")
            return self.save_response_content()

        if "text/plain" in self.content_type:
            self.set_resource_type("plain")
            return self.save_response_content()

        if "application/json" in self.content_type:
            self.set_resource_type("json")
            return self.save_response_content()

        if "application/octet-stream" in self.content_type:
            self.set_resource_type("octect-stream")
            return self.save_response_content()

        if "image/jpeg" in self.content_type:
            self.set_resource_type("jpeg")
            return self.save_response_content()

        if "image/png" in self.content_type:
            self.set_resource_type("png")
            return self.save_response_content()

        if "video/mp4" in self.content_type:
            self.set_resource_type("mp4")
            return self.save_response_content()

        if "video/x-ms-wm" in self.content_type:
            self.set_resource_type("avi")
            return self.save_response_content()

        if "text/html" in self.content_type:
            self.set_resource_type("html")
            return self.parse_html()

        if self.response.status_code % 300 < 100:
            self.url = self.response.headers["Location"]
            self.logger.warning("Redirecting to %r", self.url)
            return self.download()

        self.logger.error(
            "Content not identified: %r (code=%s, header=%r)",
            self.url,
            self.response.status_code,
            self.response.headers,
        )
        return None

    def parse_html(self):
        """Parses a HTML response."""
        self.set_resource_type("html")
        self.logger.debug("Parsing HTML (%r)", self.url)
        resource = self.soup.find("object", {"id": "resourceobject"})

        try:
            name = self.soup.find("div", {"role": "main"}).h2.text
        except AttributeError:
            # Check if it is a weird page
            if self.soup.find("applet"):
                self.logger.debug("Identified as weird page without content, skipping")
                return
            raise

        # Self does not contain the file, only a link to the real file.
        self.NOTIFY = False

        try:
            resource = Resource(
                name, self.section, resource["data"], self.icon_url, self.subject, self
            )
            self.logger.debug(
                "Created resource from HTML: %r, %s", resource.name, resource.url
            )
            self.subject.add_link(resource)
            return
        except TypeError:
            pass

        try:
            resource = self.soup.find("iframe", {"id": "resourceobject"})
            resource = Resource(
                name, self.section, resource["src"], self.icon_url, self.subject, self
            )
            self.logger.debug(
                "Created resource from HTML: %r, %s", resource.name, resource.url
            )
            self.subject.add_link(resource)
            return
        except TypeError:
            pass

        try:
            resource = self.soup.find("div", {"class": "resourceworkaround"})
            resource = Resource(
                name,
                self.section,
                resource.a["href"],
                self.icon_url,
                self.subject,
                self,
            )
            self.logger.debug(
                "Created resource from HTML: %r, %s", resource.name, resource.url
            )
            self.subject.add_link(resource)
            return
        except AttributeError:
            pass

        try:
            resource = self.soup.find("div", class_="resourcecontent resourceimg")
            resource = Resource(
                name,
                self.section,
                resource.img["src"],
                self.icon_url,
                self.subject,
                self,
            )
            self.logger.debug(
                "Created resource from HTML: %r, %s", resource.name, resource.url
            )
            self.subject.add_link(resource)
        except TypeError:
            random_name = str(random.randint(0, 1000))
            self.logger.exception("HTML ERROR (ID=%s)", random_name)
            self.logger.error("ERROR LINK: %s", self.url)
            self.logger.error("ERROR HEADS: %s", self.response.headers)

            with open(random_name + ".html", "wb") as file_handler:
                file_handler.write(self.response.content)


class Folder(BaseLink):
    """Representation of a folder."""

    NOTIFY = True

    def __init__(self, name, section, url, icon_url, subject, id_, parent=None):
        super().__init__(name, section, url, icon_url, subject, parent)
        self.id = id_

    def make_request(self):
        """Makes the request for the Link."""
        self.logger.debug("Making request")

        data = {"id": self.id, "sesskey": self.connection.sesskey}
        self.response = self.connection.post(
            self.url, timeout=GeneralSettings.timeout, data=data
        )
        self.logger.debug("Response obtained [%d]", self.response.status_code)

    def download(self):
        """Downloads the folder."""
        self.logger.debug("Downloading folder %s", self.name)
        self.make_request()
        self.save_response_content()


class BaseForum(BaseLink):
    """Representation of a Forum link."""

    BASE_DIR = "foros"

    def download(self):
        """Downloads the resources found in the forum hierarchy."""
        raise NotImplementedError


class ForumList(BaseForum):
    def download(self):
        self.logger.debug("Downloading forum list %s", self.name)
        self.make_request()
        self.process_request_bs4()

        themes = self.soup.findAll("td", {"class": "topic starter"})

        for theme in themes:
            forum = ForumDiscussion(
                theme.text,
                self.section,
                theme.a["href"],
                self.icon_url,
                self.subject,
                self,
            )

            self.logger.debug(
                "Created forum discussion from forum list: %r, %s",
                forum.name,
                forum.url,
            )
            self.subject.add_link(forum)


class ForumDiscussion(BaseForum):
    # NOTIFY = True

    def download(self):
        self.logger.debug("Downloading forum discussion %s", self.name)
        self.make_request()
        self.process_request_bs4()

        attachments = self.soup.findAll("div", {"class": "attachments"})
        images = self.soup.findAll("div", {"class": "attachedimages"})

        for attachment in attachments:
            try:
                resource = Resource(
                    Path(attachment.text).stem,
                    self.section,
                    attachment.a["href"],
                    attachment.a.img["src"],
                    self.subject,
                    self,
                )
                resource.subfolders = self.subfolders

                self.logger.debug(
                    "Created resource from forum: %r, %s", resource.name, resource.url
                )
                self.subject.add_link(resource)
            except TypeError:
                pass

        for image_container in images:
            real_images = image_container.findAll("img")
            for image in real_images:
                try:
                    url = image["href"]
                except KeyError:
                    url = image["src"]

                image_ext = Path(url).suffix[1:]
                if image_ext in ("jpg", "jpeg"):
                    icon_url = "https://campusvirtual.uva.es/invalid/f/jpeg"
                else:
                    raise RuntimeError

                resource = Resource(
                    Path(url).stem, self.section, url, icon_url, self.subject, self
                )
                resource.subfolders = self.subfolders

                self.logger.debug(
                    "Created resource (image) from forum: %r, %s",
                    resource.name,
                    resource.url,
                )
                self.subject.add_link(resource)


class Delivery(BaseLink):
    """Representation of a delivery link."""

    NOTIFY = True

    def download(self):
        """Downloads the resources found in the delivery."""
        self.logger.debug("Downloading delivery %s", self.name)
        self.make_request()
        self.process_request_bs4()

        links = []
        containers = self.soup.findAll("a", {"target": "_blank"})

        for container in containers:
            url = container["href"]
            if self.ensure_origin(url):
                icon_url = container.parent.img["src"]
                valid = True
            else:
                icon_url = self.icon_url
                valid = False

            resource = Resource(
                Path(container.text).stem,
                self.section,
                container["href"],
                icon_url,
                self.subject,
                self,
            )
            resource.subfolders = self.subfolders

            # If the resource is not in campusvirtual.uva.es, then don't include in email
            if not valid:
                resource.NOTIFY = False

            self.logger.debug(
                "Created resource from delivery: %r, %s", resource.name, resource.url
            )
            links.append(resource)

        names = [link.name for link in links]
        dupes = {x for x in names if names.count(x) > 1}
        dupes_counters = {x: 1 for x in dupes}

        if dupes:
            for i, _ in enumerate(links):
                if links[i].name in dupes:
                    name = links[i].name
                    links[i].name += "_" + str(dupes_counters[name])
                    dupes_counters[name] += 1
                    self.logger.debug("Changed name %r -> %r", name, links[i].name)

        for link in links:
            self.subject.add_link(link)
