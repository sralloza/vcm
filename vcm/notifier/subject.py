from typing import List

from vcm.downloader.subject import Subject
from vcm.notifier.link import NotifierLink

NL = List[NotifierLink]


class NotifierSubject(Subject):
    def __init__(self, name, url, connection, queue):
        super().__init__(name, url, connection, queue)
        self.new_links: NL = []
        self.determine_new_links()

    @classmethod
    def from_subject(cls, subject: Subject):
        return NotifierSubject(subject.name, subject.url, subject.connection, subject.queue)

    def determine_new_links(self):
        for link in self.notes_links:
            notifier_link = NotifierLink.from_link(link)
            result = notifier_link.save()
            if result:
                self.notes_links.append(notifier_link)
