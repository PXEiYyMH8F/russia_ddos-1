import socket
import socks
from typing import List
from ripper.common import readfile
import time


class Sock5Proxy:
    def __init__(self, host: str, port: int, username: str = None, password: str = None, rdns: bool = True):
        self.host = host
        self.port = int(port)
        self.username = username
        self.password = password
        self.rdns = rdns

    # mutates socket
    # https://pypi.org/project/PySocks/
    def decorate_socket(self, s):
        if self.username and self.password:
            s.set_proxy(socks.PROXY_TYPE_SOCKS5, self.host, self.port,
                        self.rdns, self.username, self.password)
        else:
            s.set_proxy(socks.PROXY_TYPE_SOCKS5,
                        self.host, self.port, self.rdns)
        return s

    def id(self):
        if self.username and self.password:
            return f'SOCKS5:{self.host}:{self.port}:{self.rdns}:{self.username}:{self.password}'
        else:
            return f'SOCKS5:{self.host}:{self.port}:{self.rdns}'

    def __eq__(self, other):
        if not isinstance(other, Sock5Proxy):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.host == other.host \
            and self.port == other.port \
            and self.username == other.username \
            and self.password == other.password \
            and self.rdns == other.rdns

    def validate(self):
        try:
            http_socket = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
            self.decorate_socket(http_socket)
            http_socket.settimeout(5)
            http_socket.connect(('google.com', 80))
        # except socks.ProxyError:
        except:
            return False
        return True


def read_proxy_list(filename: str) -> List[Sock5Proxy]:
    proxy_list = []
    lines = readfile(filename)
    for line in lines:
        # ip:port:username:password or ip:port
        ip, port, username, password = line.strip().split(':')
        proxy = Sock5Proxy(host=ip, port=port,
                           username=username, password=password)
        proxy_list.append(proxy)
    return proxy_list
