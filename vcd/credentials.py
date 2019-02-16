import json
import os


class Credentials:
    def __init__(self):
        self.path = 'credentials.json'
        self.credentials = []
        self.load()

    def load(self):
        if not os.path.isfile(self.path):
            self.make_example()
            self.save()
            raise RuntimeError('File not found, created sample')

        with open(self.path, encoding='utf-8') as fh:
            self.credentials = json.load(fh)

    def save(self):
        with open(self.path, 'wt', encoding='utf-8') as fh:
            json.dump(self.credentials, fh, indent=4, ensure_ascii=False)

    @staticmethod
    def get(name):
        self = Credentials.__new__(Credentials)
        self.__init__()

        for user in self.credentials:
            if user['name'] == name:
                return user

        raise RuntimeError('User not found')

    def make_example(self):
        user = {'name': 'real name or alias to use in code',
                'username': 'username of the virtual campus',
                'password': 'password of the virtual campus'}

        self.credentials.append(user)
        self.save()
