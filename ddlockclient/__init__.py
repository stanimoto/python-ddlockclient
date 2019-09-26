__version__ = '0.1.5'

import logging
import socket
import re
import time

logger = logging.getLogger(__name__)

DEFAULT_PORT = 7002


def eurl_repl(m):
    return "%%%02X" % ord(m.group(1))


def eurl(name):
    name = re.sub(r'([^a-zA-Z0-9_,.\\: -])', eurl_repl, name)
    name = re.sub(' ', '+', name)
    return name


class DDLockError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class DDLock(object):
    def __init__(self, client, name, servers=[]):
        self.client = client
        self.name = name
        self.sockets = self.getlocks(servers)

    def getlocks(self, servers):
        addrs = []

        def fail(msg):
            for addr in addrs:
                sock = self.client.get_sock(addr)
                if not sock:
                    continue
                try:
                    sock['socket'].send("releaselock lock=%s\r\n" \
                        % eurl(self.name))
                    sock['file'].readline()
                except socket.error as e:
                    logger.debug(
                        'error releasing lock on %s in fail - %s', addr, e
                    )
            raise DDLockError(msg)

        for server in servers:
            host_port = server.split(':')
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else DEFAULT_PORT
            addr = "%s:%s" % (host, port)

            sock = self.client.get_sock(addr)
            if not sock:
                continue

            data = None
            try:
                sock['socket'].send("trylock lock=%s\r\n" % eurl(self.name))
                data = sock['file'].readline()
            except socket.error as e:
                logger.debug('error getting lock on %s - %s', addr, e)

            if not (data and re.search(r'^ok\b', data, re.I)):
                fail("%s: '%s' %s\n" % (server, self.name, repr(data)))

            addrs.append(addr)

        if len(addrs) == 0:
            raise DDLockError("No available lock hosts")

        return addrs

    def release(self):
        count = 0
        for addr in self.sockets:
            sock = self.client.get_sock_onlycache(addr)
            if not sock:
                continue
            data = None
            try:
                sock['socket'].send("releaselock lock=%s\r\n" \
                    % eurl(self.name))
                data = sock['file'].readline()
            except Exception as e:
                logger.debug('error releasing lock on %s - %s', addr, e)
            if data and not re.search(r'^ok\b', data, re.I):
                raise DDLockError("releaselock (%s): %s" \
                    % (addr, repr(data)))
            count += 1

        return count

    def __enter__(self):
        return self

    def __exit__(self, type, val, tb):
        self.release()

    def __del__(self):
        try:
            self.release()
        except:
            pass


class DDLockClient(object):
    def __init__(self, servers=[]):
        self.servers = servers
        self.sockcache = {}
        self.errmsg = ""

    def get_sock_onlycache(self, addr):
        return self.sockcache.get(addr)

    def get_sock(self, addr):
        host, port = addr.split(':')

        sock = self.sockcache.get(addr)
        if sock:
            try:
                if sock['socket'].getpeername():
                    return sock
            except socket.error as e:
                logger.debug('error getting remote address %s - %s', addr, e)

            sock['socket'] = None
            del self.sockcache[addr]

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(1)

        try:
            sock.connect((host, int(port)))
            sock = {'socket': sock, 'file': sock.makefile()}
        except socket.error as e:
            logger.debug('error connecting to %s - %s', addr, e)
            return None

        self.sockcache[addr] = sock
        return sock

    def trylock(self, name, timeout=None):
        return self._trylock_wait(name, timeout)

    def _trylock(self, name):
        lock = None
        try:
            lock = DDLock(self, name, self.servers)
        except DDLockError, e:
            self.errmsg = str(e)
        except Exception, e:
            self.errmsg = "Unknown failure: %s" % str(e)

        return lock

    def _trylock_wait(self, name, timeout=None):
        lock = None
        try_until = time.time()
        if timeout is not None:
            try_until += timeout

        while not lock:
            lock = self._trylock(name)
            if lock:
                break
            if timeout is not None and time.time() > try_until:
                break
            time.sleep(0.1)

        return lock

    def last_error(self):
        return self.errmsg
