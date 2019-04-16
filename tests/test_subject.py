import os
import random
from queue import Queue

import pytest
import requests
from bs4 import BeautifulSoup as Soup

from vcd import Downloader, Subject
from vcd.alias import Alias
from vcd.links import BaseLink


def test_str(_subject):
    subject1 = _subject('test-str-1', 'http://localhost/subject-1')
    assert str(subject1) == 'test-str-1'

    subject2 = _subject('test str 2', 'http://localhost/subject-2')
    assert str(subject2) == 'Test str 2'


def test_repr(_subject):
    subject1 = _subject('test-repr-1', 'http://localhost/subject-1')
    assert repr(subject1) == "Subject(name='test-repr-1', " \
                             "url='http://localhost/subject-1', 0 notes links)"

    subject2 = _subject('Test repr 2', 'http://localhost/subject-2')
    assert repr(subject2) == "Subject(name='Test repr 2', " \
                             "url='http://localhost/subject-2', 0 notes links)"


def test_make_request(_subject):
    subject = _subject('test-make-request', 'https://www.ilovepdf.com/img/ilovepdf.svg')
    subject.make_request()

    assert subject.response.status_code == 200
    assert subject.response.content == requests.get(subject.url).content
    assert subject.soup == Soup(subject.response.content, 'html.parser')


def test_create_folder(_subject):
    subject = _subject('subject-test-create-folder')
    subject.create_folder()
    assert os.path.isdir('temp_tests/subject-test-create-folder')


def test_add_link(_subject):
    subject = _subject('test-add-link', 'asdf')
    l1 = BaseLink('link-1', '1', subject, subject.downloader, subject.queue)
    l2 = BaseLink('link-2', '2', subject, subject.downloader, subject.queue)
    l3 = BaseLink('link-3', '3', subject, subject.downloader, subject.queue)
    l4 = BaseLink('link-4', '4', subject, subject.downloader, subject.queue)
    l5 = BaseLink('link-5', '5', subject, subject.downloader, subject.queue)
    l6 = BaseLink('link-6', '6', subject, subject.downloader, subject.queue)
    l7 = BaseLink('link-7', '7', subject, subject.downloader, subject.queue)
    l8 = BaseLink('link-8', '8', subject, subject.downloader, subject.queue)
    l9 = BaseLink('link-9', '9', subject, subject.downloader, subject.queue)
    l10 = BaseLink('link-10', '10', subject, subject.downloader, subject.queue)

    assert repr(subject) == "Subject(name='test-add-link', url='asdf', 0 notes links)"
    subject.add_link(l1)
    assert repr(subject) == "Subject(name='test-add-link', url='asdf', 1 notes links)"
    subject.add_link(l2)
    assert repr(subject) == "Subject(name='test-add-link', url='asdf', 2 notes links)"
    subject.add_link(l3)
    assert repr(subject) == "Subject(name='test-add-link', url='asdf', 3 notes links)"
    subject.add_link(l4)
    assert repr(subject) == "Subject(name='test-add-link', url='asdf', 4 notes links)"
    subject.add_link(l5)
    assert repr(subject) == "Subject(name='test-add-link', url='asdf', 5 notes links)"
    subject.add_link(l6)
    assert repr(subject) == "Subject(name='test-add-link', url='asdf', 6 notes links)"
    subject.add_link(l7)
    assert repr(subject) == "Subject(name='test-add-link', url='asdf', 7 notes links)"
    subject.add_link(l8)
    assert repr(subject) == "Subject(name='test-add-link', url='asdf', 8 notes links)"
    subject.add_link(l9)
    assert repr(subject) == "Subject(name='test-add-link', url='asdf', 9 notes links)"
    subject.add_link(l10)
    assert repr(subject) == "Subject(name='test-add-link', url='asdf', 10 notes links)"

    assert l1 in subject.notes_links
    assert l2 in subject.notes_links
    assert l3 in subject.notes_links
    assert l4 in subject.notes_links
    assert l5 in subject.notes_links
    assert l6 in subject.notes_links
    assert l7 in subject.notes_links
    assert l8 in subject.notes_links
    assert l9 in subject.notes_links
    assert l10 in subject.notes_links


@pytest.fixture
def _subject(queue, d):
    def p(name, url=None):
        if url is None:
            url = str(random.randint(1, 10 ** 9))
        subject = Subject(name, url, d, queue)
        return subject

    return p


@pytest.fixture(scope='module')
def queue():
    return Queue()


@pytest.fixture(scope='module')
def d():
    return Downloader()


@pytest.fixture(autouse=True)
def controller():
    Alias.destroy()
    yield
    Alias.destroy()
