import logging
from typing import List

from vcm.downloader.subject import Subject

from .link import NotifierLink

NL = List[NotifierLink]

logger = logging.getLogger(__name__)


class NotifierSubject(Subject):
    def __init__(self, name, url, queue):
        super().__init__(name, url, queue)
        self.new_links: NL = []

    @classmethod
    def from_subject(cls, subject: Subject):
        ns = NotifierSubject(subject.name, subject.url, subject.queue)
        ns.notes_links = [x for x in subject.notes_links if x.notify]
        logger.debug("%d - %d", len(subject.notes_links), len(ns.notes_links))
        ns.determine_new_links()
        return ns

    def determine_new_links(self):
        total = 0
        for link in self.notes_links:
            notifier_link = NotifierLink.from_link(link)
            result = notifier_link.save()
            if result:
                self.new_links.append(notifier_link)
                total += 1

        logger.debug("Found %d new links of %s", total, self.name)
        return total
