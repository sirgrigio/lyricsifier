import os
import logging

log = logging.getLogger(__name__)


def mkdirs(name, safe=True):
    if safe:
        if not os.path.exists(name):
            os.makedirs(name)
    else:
        os.makedirs(name, exist_ok=True)
