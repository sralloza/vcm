import os
from threading import Thread

import pytest

from vcd.alias import Alias, IdError, AliasNotFoundError, AliasFatalError


class TestAliasExceptions:
    def test_id_error(self):
        with pytest.raises(IdError):
            raise IdError

    def test_alias_not_found_error(self):
        with pytest.raises(AliasNotFoundError):
            raise AliasNotFoundError

    def test_alias_fatal_error(self):
        with pytest.raises(AliasFatalError):
            raise AliasFatalError


def test_load():
    a = Alias()
    a.json = []
    a.save()
    del a

    a = Alias()

    assert len(a.json) == 0


def test_create_name():
    assert Alias._create_name('a', 1) == 'a.1'
    assert Alias._create_name('b', 4) == 'b.4'

    assert Alias._create_name('aaa.bbb', 23) == 'aaa.23.bbb'
    assert Alias._create_name('asdf.x', 1) == 'asdf.1.x'

    assert Alias._create_name('aaa.bbb.ccc', 1) == 'aaa.bbb.1.ccc'
    assert Alias._create_name('aaa.bbb.ccc.ddd', 1) == 'aaa.bbb.ccc.1.ddd'
    assert Alias._create_name('aaa.bbb.ccc.ddd.eee', 1) == 'aaa.bbb.ccc.ddd.1.eee'


# def test_increment():
#     a = Alias()

class TestRealToAlias:
    def test_real_to_alias_0(self):
        assert Alias.real_to_alias(0, 'real') == 'real'
        json = Alias().json
        assert len(json) == 1
        assert {'id': 0, 'new': 'real', 'old': 'real', 'type': '?'} in json

        assert Alias.real_to_alias(1, 'real') == 'real.1'
        json = Alias().json
        assert len(json) == 2
        assert {'id': 1, 'new': 'real.1', 'old': 'real', 'type': '?'} in json

        assert Alias.real_to_alias(2, 'real') == 'real.2'
        json = Alias().json
        assert len(json) == 3
        assert {'id': 2, 'new': 'real.2', 'old': 'real', 'type': '?'} in json

        assert Alias.real_to_alias(3, 'real') == 'real.3'
        json = Alias().json
        assert len(json) == 4
        assert {'id': 3, 'new': 'real.3', 'old': 'real', 'type': '?'} in json

    def test_real_to_alias_1(self):
        assert Alias.real_to_alias(10, 'aaa.bbb') == 'aaa.bbb'
        json = Alias().json
        assert {'id': 10, 'new': 'aaa.bbb', 'old': 'aaa.bbb', 'type': '?'} in json

        assert Alias.real_to_alias(11, 'aaa.bbb') == 'aaa.1.bbb'
        json = Alias().json
        assert {'id': 11, 'new': 'aaa.1.bbb', 'old': 'aaa.bbb', 'type': '?'} in json

        assert Alias.real_to_alias(12, 'aaa.bbb') == 'aaa.2.bbb'
        json = Alias().json
        assert {'id': 12, 'new': 'aaa.2.bbb', 'old': 'aaa.bbb', 'type': '?'} in json

    def test_real_to_alias_2(self):
        assert Alias.real_to_alias(20, 'aaa.bbb.ccc') == 'aaa.bbb.ccc'
        json = Alias().json
        assert {'id': 20, 'new': 'aaa.bbb.ccc', 'old': 'aaa.bbb.ccc', 'type': '?'} in json

        assert Alias.real_to_alias(21, 'aaa.bbb.ccc') == 'aaa.bbb.1.ccc'
        json = Alias().json
        assert {'id': 21, 'new': 'aaa.bbb.1.ccc', 'old': 'aaa.bbb.ccc', 'type': '?'} in json

        assert Alias.real_to_alias(22, 'aaa.bbb.ccc') == 'aaa.bbb.2.ccc'
        json = Alias().json
        assert {'id': 22, 'new': 'aaa.bbb.2.ccc', 'old': 'aaa.bbb.ccc', 'type': '?'} in json

    def test_real_to_alias_3(self):
        assert Alias.real_to_alias(30, 'aaa.bbb.ccc.ddd') == 'aaa.bbb.ccc.ddd'
        json = Alias().json
        assert {'id': 30, 'new': 'aaa.bbb.ccc.ddd', 'old': 'aaa.bbb.ccc.ddd', 'type': '?'} in json

        assert Alias.real_to_alias(21, 'aaa.bbb.ccc.ddd') == 'aaa.bbb.ccc.1.ddd'
        json = Alias().json
        assert {'id': 21, 'new': 'aaa.bbb.ccc.1.ddd', 'old': 'aaa.bbb.ccc.ddd', 'type': '?'} in json

        assert Alias.real_to_alias(22, 'aaa.bbb.ccc.ddd') == 'aaa.bbb.ccc.2.ddd'
        json = Alias().json
        assert {'id': 22, 'new': 'aaa.bbb.ccc.2.ddd', 'old': 'aaa.bbb.ccc.ddd', 'type': '?'} in json

    def test_real_to_alias_equal_ids(self):
        assert Alias.real_to_alias(100, 'whatever') == 'whatever'

        with pytest.raises(IdError, match='Same id, different names'):
            Alias.real_to_alias(100, 'other')

    def test_alias_multithreading(self):

        class Worker(Thread):
            def __init__(self, data):
                super().__init__()
                self.data = data

            def run(self):
                for data in self.data:
                    Alias.real_to_alias(*data)

        a = Alias()
        a.json = []
        a.save()

        data1 = []
        data2 = []
        test_length = 50

        expected = []
        for i, j in zip(range(test_length), range(test_length, 2 * test_length)):
            data1.append((i, f'data1-{i:03d}.txt'))
            data2.append((j, f'data2-{j:03d}.txt'))
            expected.append(
                {'id': i, 'new': f'data1-{i:03d}.txt', 'old': f'data1-{i:03d}.txt', 'type': '?'})
            expected.append(
                {'id': j, 'new': f'data2-{j:03d}.txt', 'old': f'data2-{j:03d}.txt', 'type': '?'})
            print(f'data2-{i:03d}.txt')

        t1 = Worker(data1)
        t2 = Worker(data2)

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        json = Alias().json
        json.sort(key=lambda x: x['new'])
        expected.sort(key=lambda x: x['new'])

        for element in expected:
            assert element in json

        assert len(json) == 2 * test_length


class TestAliasToReal:
    # noinspection PyDeprecation
    def test_alias_to_real_0(self):
        assert len(Alias().json) == 0
        assert Alias.real_to_alias(1, 'aaa.bbb.ccc') == 'aaa.bbb.ccc'
        assert Alias.real_to_alias(2, 'aaa.bbb.ccc') == 'aaa.bbb.1.ccc'
        assert Alias.real_to_alias(3, 'aaa.bbb.ccc') == 'aaa.bbb.2.ccc'
        assert Alias.real_to_alias(4, 'aaa.bbb.ccc') == 'aaa.bbb.3.ccc'
        assert Alias.real_to_alias(5, 'aaa.bbb.ccc') == 'aaa.bbb.4.ccc'

        assert Alias.alias_to_real('aaa.bbb.ccc') == 'aaa.bbb.ccc'
        assert Alias.alias_to_real('aaa.bbb.1.ccc') == 'aaa.bbb.ccc'
        assert Alias.alias_to_real('aaa.bbb.2.ccc') == 'aaa.bbb.ccc'
        assert Alias.alias_to_real('aaa.bbb.3.ccc') == 'aaa.bbb.ccc'

    def test_alias_to_real_not_found(self):
        assert Alias.real_to_alias(1, 'First') == 'First'
        assert Alias.real_to_alias(2, 'Second') == 'Second'

        with pytest.raises(AliasNotFoundError):
            assert Alias.alias_to_real('Third') == 'Third'

        assert Alias.real_to_alias(3, 'Third') == 'Third'
        assert Alias.alias_to_real('Third') == 'Third'


class TestGetRealFromId:
    # noinspection PyDeprecation
    def test_get_real_from_id_0(self):
        assert len(Alias().json) == 0
        assert Alias.real_to_alias(1, 'aaa.bbb.ccc') == 'aaa.bbb.ccc'
        assert Alias.real_to_alias(2, 'aaa.bbb.ccc') == 'aaa.bbb.1.ccc'
        assert Alias.real_to_alias(3, 'aaa.bbb.ccc') == 'aaa.bbb.2.ccc'
        assert Alias.real_to_alias(4, 'aaa.bbb.ccc') == 'aaa.bbb.3.ccc'
        assert Alias.real_to_alias(5, 'aaa.bbb.ccc') == 'aaa.bbb.4.ccc'

        assert Alias.get_real_from_id(1) == 'aaa.bbb.ccc'
        assert Alias.get_real_from_id(2) == 'aaa.bbb.ccc'
        assert Alias.get_real_from_id(3) == 'aaa.bbb.ccc'
        assert Alias.get_real_from_id(4) == 'aaa.bbb.ccc'

    def test_alias_to_real_not_found(self):
        assert Alias.real_to_alias(1, 'First') == 'First'
        assert Alias.real_to_alias(2, 'Second') == 'Second'

        with pytest.raises(IdError):
            assert Alias.get_real_from_id(3) == 'Third'

        assert Alias.real_to_alias(3, 'Third') == 'Third'
        assert Alias.get_real_from_id(3) == 'Third'


@pytest.fixture(scope='function', autouse=True)
def delete_alias_json():
    if os.path.isfile(Alias().alias_path):
        os.remove(Alias().alias_path)
