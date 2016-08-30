import logging
import json
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from lyricsifier.utils import connection


class BaseTagger(ABC):

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def __str__(self):
        return self.__class__.__name__

    @abstractmethod
    def tag(self, artist, title):
        pass


class LastFMTagger(BaseTagger):

    def __init__(self, api_key):
        BaseTagger.__init__(self)
        self.api_key = api_key
        self.base_url = "http://ws.audioscrobbler.com/2.0/"
        self.params = {
            'method': 'track.gettoptags',
            'artist': None,
            'track': None,
            'api_key': api_key,
            'format': 'json'
        }

    def tag(self, artist, title):
        self.params['artist'] = artist
        self.params['track'] = title
        self.log.info(
            'executing request to last.fm with params {}'.format(self.params))
        data = urllib.parse.urlencode(self.params)
        full_url = self.base_url + '?' + data
        self.log.info('requesting URL {}'.format(full_url))
        request = urllib.request.Request(full_url)
        response = connection.open(request)
        json_data = json.loads(response.read().decode('utf8'))
        self.log.debug('response {}'.format(json_data))
        error = json_data.get('error', None)
        if error:
            self.log.error(json_data['message'])
            return None
        toptags = json_data['toptags']['tag']
        return toptags[0]['name'] if toptags else None
