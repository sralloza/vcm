import os
import random
import shutil
from queue import Queue

import pytest
from bs4 import BeautifulSoup as Soup

from vcd import Subject, Downloader, Options
from vcd.alias import Alias
from vcd.links import BaseLink, Resource, Folder, Delivery


class TestBaseLink:
    # noinspection PyTypeChecker
    def test_set_post_data(self, test_link, caplog):
        data = {'username': 'foo', 'password': 'bar'}
        test_link.set_post_data(data)

        assert test_link.post_data == data
        assert str(data) in caplog.text

        with pytest.raises(TypeError, match='Expected dict, not '):
            test_link.set_post_data('')
        with pytest.raises(TypeError, match='Expected dict, not '):
            test_link.set_post_data(1 + 2j)
        with pytest.raises(TypeError, match='Expected dict, not '):
            test_link.set_post_data(5)
        with pytest.raises(TypeError, match='Expected dict, not '):
            test_link.set_post_data(6.256)
        with pytest.raises(TypeError, match='Expected dict, not '):
            test_link.set_post_data(True)

    # noinspection PyTypeChecker
    def test_set_subfolder(self, test_link, caplog):
        subfolder = 'test-subfolder'
        test_link.set_subfolder(subfolder)

        assert test_link.subfolder == subfolder
        assert str(subfolder) in caplog.text

        with pytest.raises(TypeError, match='Expected str, not '):
            test_link.set_subfolder({'user': 'foo'})
        with pytest.raises(TypeError, match='Expected str, not '):
            test_link.set_subfolder(1 + 2j)
        with pytest.raises(TypeError, match='Expected str, not '):
            test_link.set_subfolder(5)
        with pytest.raises(TypeError, match='Expected str, not '):
            test_link.set_subfolder(6.256)
        with pytest.raises(TypeError, match='Expected str, not '):
            test_link.set_subfolder(True)

    def test_create_subfolder(self, _link):
        link = _link('nets', 'nonesense')
        link.set_subfolder('subfolder')
        link.create_subfolder()

        assert os.path.isdir('temp_tests/nets/subfolder')

    def test_process_filename(self, test_link):
        assert BaseLink._process_filename('file.txt') == 'file.txt'
        assert BaseLink._process_filename('file:.txt') == 'file.txt'
        assert BaseLink._process_filename('  file:.txt') == 'file.txt'
        assert BaseLink._process_filename('?file.txt') == 'file.txt'
        assert BaseLink._process_filename('folder/file.txt') == 'folder-file.txt'
        assert BaseLink._process_filename('  file.txt  \n') == 'file.txt'
        assert BaseLink._process_filename('folder\\file.txt') == 'folder-file.txt'
        assert BaseLink._process_filename('  : file.txt') == 'file.txt'
        assert BaseLink._process_filename('*file.txt') == 'file.txt'
        assert BaseLink._process_filename('?file.txt') == 'file.txt'
        assert BaseLink._process_filename('"file.txt"') == 'file.txt'
        assert BaseLink._process_filename("'file.txt'") == 'file.txt'
        assert BaseLink._process_filename('a<b.txt') == 'a menor que b.txt'
        assert BaseLink._process_filename('a>b.txt') == 'a mayor que b.txt'
        assert BaseLink._process_filename('a|b.txt') == 'ab.txt'
        assert BaseLink._process_filename('\\') == '-'
        assert BaseLink._process_filename('/') == '-'
        assert BaseLink._process_filename('*') == ''
        assert BaseLink._process_filename(':') == ''
        assert BaseLink._process_filename('?') == ''
        assert BaseLink._process_filename('"') == ''
        assert BaseLink._process_filename("'") == ''
        assert BaseLink._process_filename('<') == ' menor que '
        assert BaseLink._process_filename('>') == ' mayor que '
        assert BaseLink._process_filename('|') == ''

    def test_filename_to_ext(self):
        assert BaseLink._filename_to_ext('a.txt') == 'txt'
        assert BaseLink._filename_to_ext('a.png') == 'png'
        assert BaseLink._filename_to_ext('a.avi') == 'avi'
        assert BaseLink._filename_to_ext('a.py') == 'py'
        assert BaseLink._filename_to_ext('a.json') == 'json'
        assert BaseLink._filename_to_ext('a.b.c.d.conf') == 'conf'
        assert BaseLink._filename_to_ext('a....pdf') == 'pdf'
        assert BaseLink._filename_to_ext('filename') == 'ukn'

    class TestGetExtFromResponse:
        @pytest.fixture(scope='class', autouse=True)
        def controller(self):
            Alias.destroy()
            yield
            Alias.destroy()

        def test_name_in_content_disposition(self, _link):
            link = _link('POND', 'wait')
            link.url = 'http://www.fundacionsgae.org/Lists/' \
                       'FSGAE_SalaPrensa_Recursos/Attachments/1/dummy.pdf'
            link.make_request()
            assert link._get_ext_from_response() == 'pdf'

        def test_name_in_url(self, _link):
            link = _link('TARDIS', 'police')
            link.url = 'https://cdn.pixabay.com/photo/2015/03/04/22/35/head-659652_960_720.png'
            link.make_request()
            assert link._get_ext_from_response() == 'png'

        def test_no_name(self, _link):
            link = _link('MELODY', 'kill')
            link.url = 'https://tomato-timer.com/'
            link.make_request()
            assert link._get_ext_from_response() == 'ukn'

        def test_name_in_content_disposition_with_subfolder(self, _link):
            link = _link('OSWALD', 'impossible')
            link.url = 'https://es.wikipedia.org/robots.txt'
            link.set_subfolder('docs')
            link.make_request()
            assert link._get_ext_from_response() == 'txt'

        def test_name_in_url_with_subfolder(self, _link):
            link = _link('RORY', 'centurion')
            link.url = 'https://support.oneskyapp.com/hc/en-us/article_attachments/' \
                       '202761627/example_1.json'
            link.set_subfolder('SPQR')
            link.make_request()
            assert link._get_ext_from_response() == 'json'

    def test_create_subject_folder(self):
        subject = Subject('test-create-folder', '', None, None)
        link = BaseLink(
            'link-create-subject-folder', '', subject, subject.downloader, subject.queue
        )
        link.create_subject_folder()

        folder_path = os.path.join(Options.ROOT_FOLDER, 'test-create-folder')

        assert os.path.isdir(folder_path)
        shutil.rmtree(folder_path)
        assert not os.path.isdir(folder_path)

    def test_make_request(self, test_link):
        test_link.url = 'http://httpbin.org/get?test=true&peter=pan'
        test_link.make_request()
        assert test_link.response.json()['args'] == {'test': 'true', 'peter': 'pan'}

        test_link.url = 'http://httpbin.org/post'
        test_link.set_post_data({'pytest': 'awesome', 'unittests': 'garbage'})
        test_link.method = 'POST'
        test_link.make_request()
        assert test_link.response.json()['form'] == {'pytest': 'awesome', 'unittests': 'garbage'}

    def test_process_request_bs4(self, test_link):
        test_link.response = test_link.downloader.get('http://www.google.es')
        test_link.process_request_bs4()

        expected = Soup(test_link.response.content, 'html.parser')
        assert test_link.soup == expected

    class TestAutosetFilepath:
        def test_exception(self, test_link):
            with pytest.raises(RuntimeError, match='Request not launched'):
                test_link.autoset_filepath()

        def test_name_in_content_disposition(self, _link):
            link = _link('POND', 'wait')
            link.url = 'http://www.fundacionsgae.org/Lists/' \
                       'FSGAE_SalaPrensa_Recursos/Attachments/1/dummy.pdf'
            link.make_request()
            assert not link.filepath
            link.autoset_filepath()
            assert link.filepath == 'temp_tests/POND/wait.pdf'

        def test_name_in_url(self, _link):
            link = _link('TARDIS', 'police')
            link.url = 'https://cdn.pixabay.com/photo/2015/03/04/22/35/head-659652_960_720.png'
            link.make_request()
            assert not link.filepath
            link.autoset_filepath()
            assert link.filepath == 'temp_tests/TARDIS/police.png'

        def test_name_in_content_disposition_with_subfolder(self, _link):
            link = _link('OSWALD', 'impossible')
            link.url = 'https://es.wikipedia.org/robots.txt'
            link.set_subfolder('docs')
            link.make_request()
            assert not link.filepath
            link.autoset_filepath()
            assert link.filepath == 'temp_tests/OSWALD/docs/impossible.txt'

        def test_name_in_url_with_subfolder(self, _link):
            link = _link('RORY', 'centurion')
            link.url = 'https://support.oneskyapp.com/hc/en-us/article_attachments/' \
                       '202761627/example_1.json'
            link.set_subfolder('SPQR')
            link.make_request()
            assert not link.filepath
            link.autoset_filepath()
            assert link.filepath == 'temp_tests/RORY/SPQR/centurion.json'

    def test_content_type(self, test_link):
        test_link.response = test_link.downloader.get('http://httpbin.org/image/jpeg')
        assert test_link.content_type == 'image/jpeg'

        test_link.response = test_link.downloader.get('http://httpbin.org/image/png')
        assert test_link.content_type == 'image/png'

        test_link.response = test_link.downloader.get('http://httpbin.org/image/svg')
        assert test_link.content_type == 'image/svg+xml'

        test_link.response = test_link.downloader.get('http://httpbin.org/image/webp')
        assert test_link.content_type == 'image/webp'

    def test_download(self, test_link):
        with pytest.raises(NotImplementedError):
            test_link.download()

    def test_get_header_length(self, test_link):
        test_link.response = test_link.downloader.get('http://httpbin.org/image/jpeg')
        assert test_link.get_header_length() == 35588

        test_link.response = test_link.downloader.get('http://httpbin.org/image/png')
        assert test_link.get_header_length() == 8090

        test_link.response = test_link.downloader.get('http://httpbin.org/image/svg')
        assert test_link.get_header_length() == 8984

        test_link.response = test_link.downloader.get('http://httpbin.org/image/webp')
        assert test_link.get_header_length() == 10568

    class TestSaveResponseContent:
        @pytest.fixture(scope='class', autouse=True)
        def controller(self):
            Alias.destroy()
            yield
            Alias.destroy()

        def test_name_in_content_disposition(self, _link):
            link = _link('POND', 'wait')
            link.url = 'http://www.fundacionsgae.org/Lists/' \
                       'FSGAE_SalaPrensa_Recursos/Attachments/1/dummy.pdf'
            link.make_request()
            link.save_response_content()
            assert link.filepath == 'temp_tests/POND/wait.pdf'
            assert os.path.isfile('temp_tests/POND/wait.pdf')

        def test_name_in_url(self, _link):
            link = _link('TARDIS', 'police')
            link.url = 'https://cdn.pixabay.com/photo/2015/03/04/22/35/head-659652_960_720.png'
            link.make_request()
            link.save_response_content()
            assert link.filepath == 'temp_tests/TARDIS/police.png'
            assert os.path.isfile('temp_tests/TARDIS/police.png')

        def test_name_in_content_disposition_with_subfolder(self, _link):
            link = _link('OSWALD', 'impossible')
            link.url = 'https://es.wikipedia.org/robots.txt'
            link.set_subfolder('docs')
            link.make_request()
            link.save_response_content()
            assert link.filepath == 'temp_tests/OSWALD/docs/impossible.txt'
            assert os.path.isfile('temp_tests/OSWALD/docs/impossible.txt')

        def test_name_in_url_with_subfolder(self, _link):
            link = _link('RORY', 'centurion')
            link.url = 'https://support.oneskyapp.com/hc/en-us/article_attachments/' \
                       '202761627/example_1.json'
            link.set_subfolder('SPQR')
            link.make_request()
            link.save_response_content()
            assert link.filepath == 'temp_tests/RORY/SPQR/centurion.json'
            assert os.path.isfile('temp_tests/RORY/SPQR/centurion.json')


class TestResource:
    @pytest.fixture(scope='class', autouse=True)
    def controller(self):
        Alias.destroy()
        yield
        Alias.destroy()

    @pytest.fixture
    def _resource(self, d, queue):
        def p(subject_name, link_name):
            subject = Subject(subject_name, str(random.randint(0, 10 ** 9)), d, queue)
            resource = Resource(link_name, str(random.randint(0, 10 ** 9)), subject, d, queue)
            return resource

        return p

    def test_name_in_content_disposition(self, _resource):
        resource = _resource('POND', 'wait')
        resource.url = 'http://www.fundacionsgae.org/Lists/' \
                       'FSGAE_SalaPrensa_Recursos/Attachments/1/dummy.pdf'
        resource.download()
        assert resource.filepath == 'temp_tests/POND/wait.pdf'
        assert os.path.isfile('temp_tests/POND/wait.pdf')

    def test_name_in_url(self, _resource):
        resource = _resource('TARDIS', 'police')
        resource.url = 'https://cdn.pixabay.com/photo/2015/03/04/22/35/head-659652_960_720.png'
        resource.download()
        assert resource.filepath == 'temp_tests/TARDIS/police.png'
        assert os.path.isfile('temp_tests/TARDIS/police.png')

    def test_name_in_content_disposition_with_subfolder(self, _resource):
        resource = _resource('OSWALD', 'impossible')
        resource.url = 'https://es.wikipedia.org/robots.txt'
        resource.set_subfolder('docs')
        resource.download()
        assert resource.filepath == 'temp_tests/OSWALD/docs/impossible.txt'
        assert os.path.isfile('temp_tests/OSWALD/docs/impossible.txt')

    def test_name_in_url_with_subfolder(self, _resource):
        resource = _resource('RORY', 'centurion')
        resource.url = 'https://support.oneskyapp.com/hc/en-us/article_attachments/' \
                       '202761627/example_1.json'
        resource.set_subfolder('SPQR')
        resource.download()
        assert resource.filepath == 'temp_tests/RORY/SPQR/centurion.json'
        assert os.path.isfile('temp_tests/RORY/SPQR/centurion.json')


class TestFolder:
    @pytest.fixture(scope='class', autouse=True)
    def controller(self):
        Alias.destroy()
        yield
        Alias.destroy()

    @pytest.fixture
    def _folder(self, d, queue):
        def p(subject_name, link_name):
            subject = Subject(subject_name, str(random.randint(0, 10 ** 9)), d, queue)
            resource = Folder(link_name, str(random.randint(0, 10 ** 9)), subject, d, queue)
            return resource

        return p

    def test_make_folder(self, _folder):
        folder = _folder('MySubject', 'Box')
        folder.make_folder()

        assert folder.subfolder == 'Box'
        assert os.path.isdir('temp_tests/MySubject/Box')


class TestDelivery:
    @pytest.fixture(scope='class', autouse=True)
    def controller(self):
        Alias.destroy()
        yield
        Alias.destroy()

    @pytest.fixture
    def _delivery(self, d, queue):
        def p(subject_name, link_name):
            subject = Subject(subject_name, str(random.randint(0, 10 ** 9)), d, queue)
            resource = Delivery(link_name, str(random.randint(0, 10 ** 9)), subject, d, queue)
            return resource

        return p

    def test_make_subfolder(self, _delivery):
        delivery = _delivery('MyDelivery', 'Box')
        delivery.make_subfolder()

        assert delivery.subfolder == 'Box'
        assert os.path.isdir('temp_tests/MyDelivery/Box')


@pytest.fixture
def queue():
    return Queue()


@pytest.fixture
def subject(d, queue):
    return Subject('test-subject', 'http://localhost/url-test-subject', d, queue)


@pytest.fixture
def d():
    return Downloader()


@pytest.fixture
def test_link(subject, queue, d):
    return BaseLink('test-name', 'http://localhost/url-test-link', subject, d, queue)


@pytest.fixture
def _link(d, queue):
    def p(subject_name, link_name):
        subject = Subject(subject_name, str(random.randint(0, 10 ** 9)), d, queue)
        link = BaseLink(link_name, str(random.randint(0, 10 ** 9)), subject, d, queue)
        return link

    return p
