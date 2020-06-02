import socket

from ._backend import Backend

class LocalBackend(Backend):
    def __init__(self):
        super().__init__()
        hostname = socket.gethostname().replace('.local','')
        self.name = hostname
        pass
