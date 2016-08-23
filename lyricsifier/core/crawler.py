import logging
import re
import urllib2
from bs4 import BeautifulSoup


class LyricsComCrawler:

    def __init__(self):
        self.baseUrl = 'http://www.lyrics.com'
        self.lyricsUrlPattern = '{:s}/{:s}-lyrics-{:s}.html'
        self.normalizingRegex = re.compile('[^a-zA-Z0-9\s-]')
        self.logger = logging.getLogger('lyricsifier.crawler.LyricsComCrawler')

    def _formatLyricsUrl(self, artist, title):
        a = re.sub(' +', '-', self.normalizingRegex.sub('', artist)).lower()
        t = re.sub(' +', '-', self.normalizingRegex.sub('', title)).lower()
        return self.lyricsUrlPattern.format(self.baseUrl, t, a)

    def crawl(self, artist, title):
        requestUrl = self._formatLyricsUrl(artist, title)
        self.logger.info('retrieving lyrics at url {:s}'.format(requestUrl))

        request = urllib2.Request(requestUrl)
        response = urllib2.urlopen(request)
        if requestUrl == response.geturl():
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            div = soup.find(id='lyrics')
            if div:
                lyrics = div.get_text().encode('utf8')
                self.logger.debug('lyrics found\n{}'.format(lyrics))
                return lyrics
            else:
                self.logger.warning('cannot find lyrics inside of html')
                return None
        else:
            self.logger.warning('redirect to {:s}'.format(response.geturl()))
            self.logger.warning('cannot find lyrics')
            return None

    def stripLyricsAuthor(self, lyrics):
        return re.sub('---\n?\s?[lL]yrics submitted by .+$', '', lyrics)


class LyricsModeCrawler:

    def __init__(self):
        self.baseUrl = 'http://www.lyricsmode.com'
        self.lyricsUrlPattern = '{:s}/lyrics/{:1}/{:s}/{:s}.html'
        self.normalizingRegex = re.compile('[^a-zA-Z0-9\s-]')
        self.logger = logging.getLogger('lyricsifier.crawler.LyricsModeCrawler')

    def _formatLyricsUrl(self, artist, title):
        a = re.sub(' +', '-', self.normalizingRegex.sub('', artist)).lower()
        t = re.sub(' +', '-', self.normalizingRegex.sub('', title)).lower()
        return self.lyricsUrlPattern.format(self.baseUrl, a[0], a, t)

    def crawl(self, artist, title):
        requestUrl = self._formatLyricsUrl(artist, title)
        self.logger.info('retrieving lyrics at url {:s}'.format(requestUrl))

        request = urllib2.Request(requestUrl)
        try:
            response = urllib2.urlopen(request)
            if requestUrl == response.geturl():
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                p = soup.find(id='lyrics_text')
                if p:
                    lyrics = p.get_text().encode('utf8')
                    self.logger.debug('lyrics found\n{}'.format(lyrics))
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
