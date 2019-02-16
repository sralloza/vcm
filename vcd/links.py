import os
import random
from queue import Queue

from bs4 import BeautifulSoup
from requests import Response

from vcd.downloader import Downloader
from vcd.globals import get_logger, FILENAME_PATTERN, ROOT_FOLDER

downloads_logger = get_logger(name='downloads', log_format='%(message)s', filename='downloads.log')


class BaseLink:
    def __init__(self, name, url, subject, downloader: Downloader,
                 queue: Queue):
        """
        Args:
            name (str): name of the url.
            url (str): URL of the url.
            subject (vcd.subject.Subject): subject of the url.
        """
        self.name = name
        self.url = url
        self.subject = subject
        self.downloader = downloader
        self.queue = queue

        self.response: Response = None
        self.soup: BeautifulSoup = None
        self.filepath: str = None
        self.method = 'GET'
        self.post_data = None
        self.redirect_url = None
        self.logger = get_logger(__name__)
        self.logger.debug('Created %s(name=%r, url=%r, subject=%r)',
                          self.__class__.__name__, self.name, self.url, self.subject.name)

    def set_post_data(self, value):
        self.logger.debug('Set post data: %r (%r)', value, self.name)
        self.post_data = value

    @staticmethod
    def _process_filename(name: str):
        return name.replace(':', '').replace('"', '').replace('/', '-').strip()

    def _get_ext_from_request(self):
        try:
            return FILENAME_PATTERN.search(
                self.response.headers['Content-Disposition']).group(1).split('.')[-1]
        except KeyError:
            self.logger.critical('Request does not contain a file (name=%r, url=%r,headers=%r)',
                                 self.name, self.url, self.response.headers)
            return 'unknown'

    def make_request(self):
        self.logger.debug('Making request')

        if self.method is None:
            raise NotImplementedError
        elif self.method == 'GET':
            self.response = self.downloader.get(self.redirect_url or self.url)

        elif self.method == 'POST':
            self.response = self.downloader.get(self.redirect_url or self.url, data=self.post_data)
        else:
            raise RuntimeError(f'Invalid method: {self.method}')

        self.logger.debug('Response obtained (%s) [%d]', self.method, self.response.status_code)

    def process_request_bs4(self):
        self.soup = BeautifulSoup(self.response.text, 'html.parser')
        self.logger.debug('Response parsed')

    def autoset_filepath(self):
        if self.response is None:
            raise RuntimeError('Request not launched')

        filename = self._process_filename(self.name) + '.' + self._get_ext_from_request()
        self.filepath = os.path.join(self.subject.name, filename)
        self.filepath = os.path.join(ROOT_FOLDER, self.filepath).replace('\\', '/')

        self.logger.debug('Set filepath: %r', self.filepath)

    def download(self):
        self.logger.debug('Called download() but it was not implemented')
        raise NotImplementedError

    def save_response_content(self):
        if self.filepath is None:
            self.autoset_filepath()

        self.subject.create_folder()

        downloads_logger.info('Downloaded %s -- %s', self.subject.name,
                              os.path.basename(self.filepath))

        try:
            with open(self.filepath, 'wb') as f:
                f.write(self.response.content)
            self.logger.debug('File downloaded and saved: %s', self.filepath)
        except PermissionError:
            self.logger.warning('File couldn\'t be downloaded due to permission error: %s',
                                os.path.basename(self.filepath))
            self.logger.warning('Permission error %s -- %s', self.subject.name,
                                os.path.basename(self.filepath))


class Resource(BaseLink):
    def __init__(self, name, url, subject, downloader: Downloader, queue: Queue):
        super().__init__(name, url, subject, downloader, queue)
        self.resource_type = 'unknown'

    def set_resource_type(self, new):
        self.logger.debug('Set resource type: %r', new)
        self.resource_type = new

        if self.resource_type == 'html':
            self.process_request_bs4()

    # def save_response_content(self):
    #     self.logger.debug('Saving file: %s', self.resource_type)
    #     print('Saving file:', self.resource_type)
    #     super().save_response_content()
    #     self.logger.debug('Filed saved: %s', self.resource_type)
    #     print('Filed saved:', self.resource_type)

    def download(self):
        self.logger.debug('Downloading resource %s', self.name)
        self.make_request()

        if self.response.status_code == 404:
            self.logger.error('status code of 404 in url %r [%r]', self.url, self.name)
            return

        if 'application/pdf' in self.response.headers['Content-Type']:
            self.set_resource_type('pdf')
            return self.save_response_content()

        elif 'officedocument.wordprocessingml.document' in self.response.headers['Content-Type']:
            self.set_resource_type('word')
            return self.save_response_content()

        elif 'msword' in self.response.headers['Content-Type']:
            self.set_resource_type('word')
            return self.save_response_content()

        elif 'application/zip' in self.response.headers['Content-Type']:
            self.set_resource_type('zip')
            return self.save_response_content()

        elif 'application/g-zip' in self.response.headers['Content-Type']:
            self.set_resource_type('gzip')
            return self.save_response_content()

        elif 'application/x-7z-compressed' in self.response.headers['Content-Type']:
            self.set_resource_type('7zip')
            return self.save_response_content()

        elif 'text/plain' in self.response.headers['Content-Type']:
            self.set_resource_type('plain')
            return self.save_response_content()

        elif 'application/octet-stream' in self.response.headers['Content-Type']:
            self.set_resource_type('octect-stream')
            return self.save_response_content()

        elif 'text/html' in self.response.headers['Content-Type']:
            self.set_resource_type('html')
            return self.parse_html()

        elif self.response.status_code % 300 < 100:
            self.url = self.response.headers['Location']
            self.logger.warning('Redirecting to %r', self.url)
            return self.download()
        else:
            self.logger.error('Content not identified: %r (code=%s, header=%r)',
                              self.url, self.response.status_code, self.response.headers)

    def parse_html(self):
        self.set_resource_type('html')
        self.logger.debug('Parsing HTML (%r)', self.url)
        resource = self.soup.find('object', {'id': 'resourceobject'})
        name = self.soup.find('div', {'role': 'main'}).h2.text

        try:
            resource = Resource(name, resource['data'], self.subject, self.downloader, self.queue)
            self.logger.debug('Created resource from HTML: %r, %s', resource.name, resource.url)
            self.subject.queue.put(resource)
            return
        except TypeError:
            pass

        try:
            resource = self.soup.find('iframe', {'id': 'resourceobject'})
            resource = Resource(name, resource['src'], self.subject, self.downloader, self.queue)
            self.logger.debug('Created resource from HTML: %r, %s', resource.name, resource.url)
            self.subject.queue.put(resource)
            return
        except TypeError:
            random_name = str(random.randint(0, 1000))
            self.logger.exception('HTML ERROR (ID=%s)', random_name)
            self.logger.error('ERROR LINK: %s', self.url)
            self.logger.error('ERROR HEADS: %s', self.response.headers)

            with open(random_name + '.html', 'wb') as fh:
                fh.write(self.response.content)

    def download_octect_stream(self):
        self.set_resource_type('octect-stream')
        self.save_response_content()


class Folder(BaseLink):
    def download(self):
        self.logger.debug('Downloading folder %s', self.name)
        self.make_request()
        self.process_request_bs4()

        try:
            form = self.soup.find('form', {'method': 'post'})
            link = form['action']
            post_id = form.find('input', {'name': 'id'})['value']
            sesskey = form.find('input', {'name': 'sesskey'})['value']
        except TypeError as ex:
            random_name = str(random.randint(0, 1000))
            self.logger.error('FOLDER ERROR (ID=%s)', random_name)
            self.logger.exception('EXCEPTION: %s', ex, exc_info=True)
            self.logger.error('ERROR LINK: %s', self.url)
            self.logger.error('ERROR HEADS: %s', self.response.headers)

            with open(random_name + '.html', 'wb') as fh:
                fh.write(self.response.content)

            return

        resource = Resource(self.name, link, self.subject, self.downloader, self.queue)
        resource.method = 'POST'
        self.logger.debug('Created resource from folder: %r, %s', resource.name, resource.url)
        resource.set_post_data({'id': post_id, 'sesskey': sesskey})

        return resource.download()


class Forum(BaseLink):
    def download(self):
        self.logger.debug('Downloading forum %s', self.name)
        self.make_request()
        self.process_request_bs4()

        if 'view.php' in self.url:
            self.logger.debug('Forum is type list of themes')
            themes = self.soup.findAll('td', {'class': 'topic starter'})

            for theme in themes:
                forum = Forum(theme.text, theme.a['href'], self.subject, self.downloader,
                              self.queue)
                self.logger.debug('Created forum from forum: %r, %s', forum.name, forum.url)
                self.queue.put(forum)

        elif 'discuss.php' in self.url:
            self.logger.debug('Forum is a theme discussion')
            attachments = self.soup.findAll('div', {'class': 'attachments'})

            for attachment in attachments:
                try:
                    resource = Resource(os.path.splitext(attachment.text)[0], attachment.a['href'],
                                        self.subject, self.downloader, self.queue)
                    self.logger.debug('Created resource from forum: %r, %s', resource.name,
                                      resource.url)
                    self.queue.put(resource)
                except TypeError:
                    continue
        else:
            self.logger.critical('Unkown url for forum %r. Vars: %r', self.url, vars())
            raise RuntimeError('Unknown url for forum: %r', self.url)


class Delivery(BaseLink):
    def download(self):
        self.logger.debug('Downloading delivery %s', self.name)
        self.make_request()
        self.process_request_bs4()

        links = []
        containers = self.soup.findAll('a', {'target': '_blank'})

        for container in containers:
            resource = Resource(os.path.splitext(container.text)[0], container['href'],
                                self.subject, self.downloader, self.queue)
            self.logger.debug('Created resource from delivery: %r, %s', resource.name,
                              resource.url)
            links.append(resource)

        names = [link.name for link in links]
        dupes = {x for x in names if names.count(x) > 1}
        dupes_counters = {x: 1 for x in dupes}

        if len(dupes) > 0:
            for i, _ in enumerate(links):
                if links[i].name in dupes:
                    name = links[i].name
                    links[i].name += '_' + str(dupes_counters[name])
                    dupes_counters[name] += 1
                    self.logger.debug('Changed name %r -> %r', name, links[i].name)

        for link in links:
            self.queue.put(link)
