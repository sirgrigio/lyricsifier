import csv
import logging
import os
import re
import urllib.request
import urllib.error
from bs4 import BeautifulSoup


class LyricsComCrawler:

    def __init__(self):
        self.baseUrl = 'http://www.lyrics.com'
        self.lyricsUrlPattern = '{:s}/{:s}-lyrics-{:s}.html'
        self.normalizingRegex = re.compile('[^a-zA-Z0-9\s-]')
        self.logger = logging.getLogger('lyricsifier.crawler.LyricsComCrawler')

    def _formatLyricsUrl(self, artist, title):
        a = re.sub(' +', '-', self.normalizingRegex.sub('', artist))
        t = re.sub(' +', '-', self.normalizingRegex.sub('', title))
        a = a.strip('-').lower()
        t = t.strip('-').lower()
        return self.lyricsUrlPattern.format(self.baseUrl, t, a)

    def crawl(self, artist, title):
        requestUrl = self._formatLyricsUrl(artist, title)
        self.logger.info('retrieving lyrics at url {:s}'.format(requestUrl))

        request = urllib.request.Request(requestUrl)
        response = urllib.request.urlopen(request)
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
        self.requestHeaders = {'User-Agent': 'Mozilla/5.0'}
        self.lyricsUrlPattern = '{:s}/lyrics/{:1}/{:s}/{:s}.html'
        self.normalizingRegex = re.compile('[^a-zA-Z0-9\s_]')
        self.logger = logging.getLogger('lyricsifier.crawler.LyricsModeCrawler')

    def _formatLyricsUrl(self, artist, title):
        a = re.sub('[\.-/]', '_', artist)
        t = re.sub('[\.-/]', '_', title)
        t = re.sub(' +', '_', self.normalizingRegex.sub('', t))
        a = re.sub('_+', '_', a)
        t = re.sub('_+', '_', t)
        a = a.strip('_').lower()
        t = t.strip('_').lower()
        return self.lyricsUrlPattern.format(self.baseUrl, a[0], a, t)

    def crawl(self, artist, title):
        requestUrl = self._formatLyricsUrl(artist, title)
        self.logger.info('retrieving lyrics at url {:s}'.format(requestUrl))

        request = urllib.request.Request(requestUrl, headers=self.requestHeaders)
        try:
            response = urllib.request.urlopen(request)
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
        except urllib.error.HTTPError as error:
            if error.code == 404:
                self.logger.warning('error 404')
                self.logger.warning('cannor find lyrics')
                return None
            else:
                raise error

    def stripLyricsAuthor(self, lyrics):
        return lyrics


class CrawlJob:

    __crawlers__ = [LyricsComCrawler(), LyricsModeCrawler(), ]

    def __init__(self, tsv, outdir, crawlers=__crawlers__, attempts=3):
        self.fin = tsv
        self.fout = os.path.join(outdir, 'lyrics.txt')
        self.crawlers = crawlers
        self.attempts = attempts
        self.outTsvFields = ['trackid', 'lyrics']
        self.normalizingRegex = re.compile('[^a-zA-Z0-9]')
        self.logger = logging.getLogger('lyricsifier.crawler.CrawlJob')
        if not os.path.exists(outdir):
            self.logger.warning('output directory does not exist - creating it...')
            os.makedirs(outdir)

    def _inline(self, lyrics):
        l = self.normalizingRegex.sub(' ', lyrics)
        return re.sub(' +', ' ', l).lower()

    def run(self):
        with open(self.fin, 'r', encoding='utf8') as tsvin, open(self.fout, 'w', encoding='utf8') as tsvout:
            reader = csv.DictReader(tsvin, delimiter='\t')
            writer = csv.DictWriter(tsvout, delimiter='\t', fieldnames=self.outTsvFields)
            writer.writeheader()
            self.logger.info('output file at {}'.format(os.path.abspath(self.fin)))
            count = 0
            found = 0
            for row in reader:
                count += 1
                self.logger.info('reading row {:d}'.format(count))
                id = row['trackid']
                artist = row['artist']
                title = row['title']
                self.logger.info('processing track {} (artist: {}, title: {})'.format(id, artist, title))
                if not id or not artist or not title:
                    self.logger.warning('incomplete data - skipping track')
                else:
                    for crawler in self.crawlers:
                        i = 0
                        error = True
                        lyrics = None
                        while error and i < self.attempts: 
                            try:
                                i += 1
                                self.logger.info('attempt {:d} with {}'.format(i, crawler))
                                lyrics = crawler.crawl(artist, title)
                                error = False
                            except urllib.error.HTTPError as e:
                                self.logger.error('error {} {}'.format(e.code, e.reason))
                        if lyrics:
                            self.logger.info('lyrics for {} retrieved by {}'.format(id, crawler))
                            lyrics = self._inline(crawler.stripLyricsAuthor(lyrics.decode('utf8')))
                            self.logger.debug('postprocessing - {}'.format(lyrics))
                            writer.writerow({'trackid': id, 'lyrics': lyrics})
                            self.logger.info('lyrics for {} written to output file'.format(id))
                            found += 1
                            break
                        else:
                            self.logger.warning('{} cannot retrieve lyrics'.format(crawler))
                self.logger.info('found {:d} lyrics out of {:d} tracks'.format(found, count))
            self.logger.info('job completed')
