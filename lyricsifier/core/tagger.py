import logging
import json
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from unidecode import unidecode
from lyricsifier.core.utils import connection


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

    def __init__(self, api_key, genres):
        BaseTagger.__init__(self)
        self.api_key = api_key
        self.base_url = "http://ws.audioscrobbler.com/2.0/"
        self.genres = genres

    def _topGenres(self):
        return {g: 0 for g in self.genres}

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
        return json_data['toptags']['tag']

    def _best(self, tags):
        if not tags:
            return None
        topGenres = self._topGenres()
        for tag in tags:
            t = unidecode(tag['name']).lower()
            c = int(tag['count'])
            for g in topGenres:
                if t == g or t in self.genres[g]:
                    topGenres[g] += c
                    break
        return max(topGenres, key=lambda g: topGenres[g])

    def tagArtist(self, artist):
        params = {
            'method': 'artist.gettoptags',
            'artist': artist,
            'api_key': self.api_key,
            'format': 'json'
        }
        response = self._request(params)
        tags = self._parse(response)
        return self._best(tags)

    def tagTrack(self, artist, title):
        params = {
            'method': 'track.gettoptags',
            'artist': artist,
            'track': title,
            'api_key': self.api_key,
            'format': 'json'
        }
        response = self._request(params)
        tags = self._parse(response)
        return self._best(tags)
