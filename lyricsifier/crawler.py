import logging
import urllib2
from bs4 import BeautifulSoup


class LyricsComCrawler:

    def __init__(self):
        self.baseUrl = 'http://www.lyrics.com'
        self.lyricsUrlPattern = '{:s}/{:s}-lyrics-{:s}.html'
        self.logger = logging.getLogger('lyricsifier.crawler.LyricsComCrawler')

    def _formatLyricsUrl(self, artist, song):
        a = artist.lower().replace(' ', '-')
        s = song.lower().replace(' ', '-')
        return self.lyricsUrlPattern.format(self.baseUrl, s, a)

    def crawl(self, artist, song):
        requestUrl = self._formatLyricsUrl(artist, song)
        self.logger.info('retrieving lyrics at url {:s}'.format(requestUrl))

        request = urllib2.Request(requestUrl)
        response = urllib2.urlopen(request)
        if requestUrl == response.geturl():
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            div = soup.find(id='lyrics')
            if div:
                lyrics = div.get_text()
                self.logger.debug('lyrics found\n{:s}'.format(lyrics))
                return lyrics
            else:
                self.logger.warning('cannot find lyrics inside of html')
                return None
        else:
            self.logger.warning('redirect to {:s}'.format(response.geturl()))
            self.logger.warning('cannot find lyrics')
            return None


class LyricsModeCrawler:

    def __init__(self):
        self.baseUrl = 'http://www.lyricsmode.com'
        self.lyricsUrlPattern = '{:s}/lyrics/{:1}/{:s}/{:s}.html'
        self.logger = logging.getLogger('lyricsifier.crawler.LyricsModeCrawler')

    def _formatLyricsUrl(self, artist, song):
        a = artist.lower().replace(' ', '_')
        s = song.lower().replace(' ', '_')
        return self.lyricsUrlPattern.format(self.baseUrl, a[0], a, s)

    def crawl(self, artist, song):
        requestUrl = self._formatLyricsUrl(artist, song)
        self.logger.info('retrieving lyrics at url {:s}'.format(requestUrl))

        request = urllib2.Request(requestUrl)
        try:
            response = urllib2.urlopen(request)
            if requestUrl == response.geturl():
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                p = soup.find(id='lyrics_text')
                if p:
                    lyrics = p.get_text()
                    self.logger.debug('lyrics found\n{:s}'.format(lyrics))
                    return lyrics
                else:
                    self.logger.warning('cannot find lyrics inside of html')
                    return None
            else:
                self.logger.warning('redirect to {:s}'.format(response.geturl()))
                self.logger.warning('cannot find lyrics')
                return None
        except urllib2.HTTPError as error:
            if error.code == 404:
                self.logger.warning('error 404')
                self.logger.warning('cannor find lyrics')
                return None
            else:
                raise error
