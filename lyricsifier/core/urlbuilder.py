import logging
import re
from abc import ABC, abstractmethod
from unidecode import unidecode


class BaseURLBuilder(ABC):

    def __init__(self, pattern):
        self.pattern = pattern
        self.log = logging.getLogger(__name__)

    def __str__(self):
        return self.__class__.__name__

    @abstractmethod
    def build(artist, title):
        pass


class MetroLyricsURLBuilder(BaseURLBuilder):

    def __init__(self):
        BaseURLBuilder.__init__(
            self,
            'http://www.metrolyrics.com/{:s}-lyrics-{:s}.html'
        )

    def _normalize(self, string):
        s = unidecode(string)
        s = re.sub('[^a-zA-Z0-9\s-]', '', s)
        s = re.sub(' +', '-', s)
        return s.strip('-').lower()

    def build(self, artist, title):
        a = self._normalize(artist)
        t = self._normalize(title)
        return self.pattern.format(t, a)


class LyricsComURLBuilder(BaseURLBuilder):

    def __init__(self):
        BaseURLBuilder.__init__(
            self,
            'http://www.lyrics.com/{:s}-lyrics-{:s}.html'
        )

    def _normalize(self, string):
        s = unidecode(string)
        s = re.sub('[^a-zA-Z0-9\s-]', '', s)
        s = re.sub(' +', '-', s)
        return s.strip('-').lower()

    def build(self, artist, title):
        a = self._normalize(artist)
        t = self._normalize(title)
        return self.pattern.format(t, a)


class LyricsModeURLBuilder(BaseURLBuilder):

    def __init__(self):
        BaseURLBuilder.__init__(
            self,
            'http://www.lyricsmode.com/lyrics/{:s}/{:s}/{:s}.html'
        )

    def _normalize(self, string):
        s = unidecode(string)
        s = re.sub('[\.-/]', '_', s)
        s = re.sub('[^a-zA-Z0-9\s_]', '', s)
        s = re.sub(' +', '_', s)
        s = re.sub('_+', '_', s)
        return s.strip('_').lower()

    def build(self, artist, title):
        a = self._normalize(artist)
        t = self._normalize(title)
        i = a[0] if len(a) > 0 and re.match('[a-z]', a[0]) else '0-9'
        return self.pattern.format(i, a, t)


class AZLyricsURLBuilder(BaseURLBuilder):

    def __init__(self):
        BaseURLBuilder.__init__(
            self,
            'http://www.azlyrics.com/lyrics/{:s}/{:s}.html'
        )

    def _normalize(self, string):
        s = unidecode(string)
        s = re.sub('[^a-zA-Z0-9]', '', s)
        return s.lower()

    def build(self, artist, title):
        a = self._normalize(artist)
        t = self._normalize(title)
        return self.pattern.format(a, t)
