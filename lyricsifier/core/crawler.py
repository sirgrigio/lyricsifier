import csv
import logging
import os
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

    def stripLyricsAuthor(self, lyrics):
        return lyrics


class CrawlJob:

    def __init__(self, tsv, outdir, crawlers=[LyricsComCrawler(), ]):
        self.fin = tsv
        self.fout = os.path.join(outdir, 'lyrics.txt')
        self.crawlers = crawlers
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
        with open(self.fin, 'rb') as tsvin, open(self.fout, 'wb') as tsvout:
            reader = csv.DictReader(tsvin, delimiter='\t')
            writer = csv.DictWriter(tsvout, delimiter='\t', fieldnames=self.outTsvFields)
            writer.writeheader()
            self.logger.info('output file at {}'.format(os.path.abspath(self.fin)))
            count = 0
            found = 0
            for row in reader:
                self.logger.info('reading row {:d}'.format(count))
                id = row['trackid']
                artist = row['artist']
                title = row['title']
                self.logger.info('processing track {} (artist: {}, title: {})'.format(id, artist, title))
                for crawler in self.crawlers:
                    lyrics = crawler.crawl(artist, title)
                    if lyrics:
                        self.logger.info('lyrics for {} retrieved by {}'.format(id, crawler))
                        lyrics = self._inline(crawler.stripLyricsAuthor(lyrics))
                        self.logger.debug('postprocessing - {}'.format(lyrics))
                        writer.writerow({'trackid': id, 'lyrics': lyrics})
                        self.logger.info('lyrics for {} written to output file'.format(id))
                        found += 1
                        self.logger.info('currently {} lyrics found'.format(found))
                        break
                    else:
                        self.logger.warning('{} cannot retrieve lyrics'.format(crawler))
                count += 1
            self.logger.info('found {:d} lyrics out of {:d} tracks'.format(found, count))
            self.logger.info('job completed')
