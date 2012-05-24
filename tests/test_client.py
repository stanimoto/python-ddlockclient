import unittest
import re
from ddlockclient import DDLockClient, DDLock, eurl

servers = ['localhost']


class TestError(Exception):
    pass


class ClientTest(unittest.TestCase):

    def setUp(self):
        self.c = DDLockClient(servers=servers)

    def _lock(self, name):
        return self.c.trylock(name, 0)  # no block

    def test_init(self):
        self.assertTrue(isinstance(self.c, DDLockClient),
                        "Got a client object")

    def test_a(self):
        lock = self._lock('test_a')
        self.assertTrue(isinstance(lock, DDLock),
                        "Got a lock for 'test_a'")

    def test_a2(self):
        lock = self._lock('test_a')
        self.assertTrue(isinstance(lock, DDLock),
                        "Got a lock for 'test_a' again")

    def test_b(self):
        lock = self._lock('test_b')
        self.assertTrue(isinstance(lock, DDLock),
                        "Got a lock for 'test_b'")
        rv = lock.release()
        self.assertTrue(rv, "Lock release succeeded")

        rv = None
        try:
            rv = lock.release()
            self.fail("Expected an error")
        except Exception, e:
            self.assertTrue(re.search('ERR didnthave',
                            str(e)),
                            "release() die if it couldn't release")
        self.assertEquals(rv, None, "no return value")

        lock2 = self._lock('test_b')
        self.assertTrue(isinstance(lock2, DDLock),
                        "Got a lock for 'test_b' again")

    def test_c(self):
        lock = self._lock('test_c')
        self.assertTrue(isinstance(lock, DDLock),
                        "Got a lock for 'test_c'")
        lock2 = self._lock('test_c')
        self.assertEquals(lock2,
                          None,
                          "Got no lock for 'test_c' again without release")

    def test_d(self):
        lock = self._lock('test_d')
        self.assertTrue(isinstance(lock, DDLock),
                        "Got a lock for 'test_d'")
        # a lock will be released when going out of with statement
        with lock:
            pass

        lock2 = self._lock('test_d')
        self.assertTrue(isinstance(lock2, DDLock),
                        "Got a lock for 'test_d' again")

    def test_e(self):
        lock = self._lock('test')
        self.assertTrue(isinstance(lock, DDLock),
                        "Got a lock for 'test'")
        try:
            raise TestError("test error")
        except Exception, e:
            self.assertTrue(isinstance(e, TestError))
        finally:
            lock.release()

        lock = self._lock('test')
        self.assertTrue(isinstance(lock, DDLock),
                        "able to lock 'test' again")

    def test_eurl(self):
        name = eurl('foo|bar')
        self.assertEqual(name, "foo%7Cbar")
        name = eurl('foo|bar/baz')
        self.assertEqual(name, "foo%7Cbar%2Fbaz")
