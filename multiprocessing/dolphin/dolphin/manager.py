import time
from multiprocessing.managers import SyncManager

_MANAGER = None
_AUTHKEY = b'a67#fa0901Sa7afZc0cb991a3eKb5-b(cbcc5575'


def get_manager():
    global _MANAGER
    if _MANAGER is None:
        # TODO: should come from config
        address = 'localhost', 6789
        _MANAGER = SyncManager(address, authkey=_AUTHKEY)
    return _MANAGER


def get_server():
    return get_manager().get_server()


def serve_forever():
    server = get_server()
    server.serve_forever()


