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
    def tagArtist(self, artist):
        pass

    @abstractmethod
    def tagTrack(self, artist, title):
        pass


class LastFMTagger(BaseTagger):

    def __init__(self, api_key):
        BaseTagger.__init__(self)
        self.api_key = api_key
        self.base_url = "http://ws.audioscrobbler.com/2.0/"

    def _request(self, params):
        self.log.info(
            'executing request to last.fm with params {}'.format(params))
        data = urllib.parse.urlencode(params)
        full_url = self.base_url + '?' + data
        self.log.info('requesting URL {}'.format(full_url))
        request = urllib.request.Request(full_url)
        return connection.open(request)

    def _parse(self, response):
        json_data = json.loads(response.read().decode('utf8'))
        self.log.debug('response {}'.format(json_data))
        error = json_data.get('error', None)
        if error:
            self.log.error(json_data['message'])
            return None
        toptags = json_data['toptags']['tag']
        return toptags[0]['name'] if toptags else None

    def tagArtist(self, artist):
        params = {
            'method': 'artist.gettoptags',
            'artist': artist,
            'api_key': self.api_key,
            'format': 'json'
        }
        response = self._request(params)
        return self._parse(response)

    def tagTrack(self, artist, title):
        params = {
            'method': 'track.gettoptags',
            'artist': artist,
            'track': title,
            'api_key': self.api_key,
            'format': 'json'
        }
        response = self._request(params)
        return self._parse(response)
