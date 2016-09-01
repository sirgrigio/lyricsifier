import errno
import logging
import urllib.request
import urllib.error

log = logging.getLogger(__name__)
__temporary_errors_codes__ = [408, 500, 503, 504]


class SOFTConnError(Exception):
    pass


class FATALConnError(Exception):
    pass


def open(request):
    try:
        return urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        if e.code in __temporary_errors_codes__:
            raise SOFTConnError(e)
        else:
            raise FATALConnError(e)
    except urllib.error.URLError as e:
        raise SOFTConnError(e)
    except OSError as e:
        if (e.errno == errno.ECONNRESET or
           e.errno == errno.ETIMEDOUT or
           e.errno == errno.ECONNABORTED):
            raise SOFTConnError(e)
        else:
            raise FATALConnError(e)
