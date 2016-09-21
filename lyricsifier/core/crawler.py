import csv
import logging
import os
import re
import time
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
from string import ascii_lowercase
from lyricsifier.core.utils import connection, file, normalization as nutils
from lyricsifier.core.utils.connection import SOFTConnError, FATALConnError


class MetroLyricsCrawler:

    def __init__(self, fout, max_delay, max_depth=100):
        self.base_url = 'http://www.metrolyrics.com'
        self.artists_index = ['1'] + list(ascii_lowercase)
        self.artists_page_pattern = self.base_url + '/artists-{:s}-{:d}.html'
        self.fout = fout
        self.max_delay = max_delay
        self.max_depth = max_depth
        self.currid = 0
        self.tsv_headers = ['trackid', 'url', 'artist', 'title']
        self.log = logging.getLogger(__name__)

    def _setUp(self):
        self.log.info('setting up')
        file.mkdirs(os.path.dirname(self.fout), safe=True)
        with open(self.fout, 'w', encoding='utf8') as tsvout:
            writer = csv.DictWriter(tsvout,
                                    delimiter='\t',
                                    fieldnames=self.tsv_headers)
            writer.writeheader()
        self.log.debug('max delay: {:d}'.format(self.max_delay))
        self.log.debug('max depth: {:d}'.format(self.max_depth))
        self.log.debug('output file: {:s}'.format(self.fout))

    def _batchWrite(self, rows):
        with open(self.fout, 'a', encoding='utf8') as tsvout:
            self.log.info('writing rows to file {:s}'.format(self.fout))
            writer = csv.DictWriter(tsvout,
                                    delimiter='\t',
                                    fieldnames=self.tsv_headers)
            writer.writerows(rows)

    def _request(self, url):
        self.log.info('requesting URL {:s}'.format(url))
        return urllib.request.Request(url)

    def _sleep(self, secs):
        self.log.warning(
            'going to sleep for {:d} seconds'.format(secs))
        time.sleep(secs)

    def _open(self, request):
        delay = 1
        while delay < self.max_delay:
            try:
                return connection.open(request)
            except SOFTConnError as e:
                self.log.error(e)
                delay *= 2
                self._sleep(delay)
            except FATALConnError as e:
                self.log.error(e)
                return None
        return None

    def _requestArtistsPage(self, idx, page):
        url = self.artists_page_pattern.format(str(idx), page)
        request = self._request(url)
        return url, self._open(request)

    def _requestSongsPage(self, pattern, page):
        url = pattern.format(page)
        request = self._request(url)
        return url, self._open(request)

    def _extractArtistName(self, a_elem):
        text = nutils.encode(a_elem.get_text())
        name = nutils.rreplace(text, b' Lyrics', b'').strip(b'\n\r\s\t')
        self.log.debug(
            'artist name {} extracted from {:s}'.format(
                nutils.decode(name), a_elem.prettify()))
        return name

    def _extractArtistSongsPagePattern(self, a_elem):
        href = a_elem['href']
        pattern = re.sub('-lyrics.html$', '-alpage-{}.html', href)
        self.log.debug(
            'songs page pattern {:s} extracted from {:s}'.format(
                pattern, a_elem.prettify()))
        return pattern

    def _extractSongTitle(self, a_elem):
        text = nutils.encode(a_elem.get_text())
        title = nutils.rreplace(
            text, b' Lyrics', b'').strip(b'\n\r\s\t')
        self.log.debug(
            'song title {} extracted from {:s}'.format(
                nutils.decode(title), a_elem.prettify()))
        return title

    def _parseSongsTable(self, artist, table):
        self.log.info('parsing songs table')
        output_rows = []
        for row in table.tbody.findAll('tr'):
            song_a = row.find('td', class_=None).find_next('a', href=True)
            title = self._extractSongTitle(song_a)
            lyrics_url = song_a['href']
            output_rows.append(
                {'trackid': self.currid + 1,
                 'url': lyrics_url,
                 'artist': nutils.decode(artist),
                 'title': nutils.decode(title)}
            )
            self.currid += 1
            self.log.info('new lyrics URL crawled - {:s}'.format(lyrics_url))
        self._batchWrite(output_rows)

    def _parseArtistsTable(self, table):
        self.log.info('parsing artists table')
        for row in table.tbody.findAll('tr'):
            artist_a = row.find('td').find_next('a', href=True)
            artist = self._extractArtistName(artist_a)
            songs_pattern = self._extractArtistSongsPagePattern(artist_a)
            page = 1
            url, response = self._requestSongsPage(songs_pattern, page)
            while response and url == response.geturl():
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table', class_='songs-table compact')
                if table:
                    self._parseSongsTable(artist, table)
                else:
                    self.log.warning(
                        'cannot crawl from {:s} - skipping'.format(url))
                page += 1
                if page > self.max_depth:
                    self.log.warning('reached max depth - skipping')
                    break
                url, response = self._requestSongsPage(songs_pattern, page)
            if response:
                self.log.info(
                    'no more songs for artist {:s}'.format(
                        nutils.decode(artist)))
            else:
                self.log.warning('cannot open URL {:s} - skipping'.format(url))

    def _browse(self):
        for idx in self.artists_index:
            self.log.info('crawling index \'{:s}\''.format(idx))
            page = 1
            url, response = self._requestArtistsPage(idx, page)
            while response and url == response.geturl():
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table', class_='songs-table')
                if table:
                    self._parseArtistsTable(table)
                else:
                    self.log.warning(
                        'cannot crawl from {:s} - skipping'.format(url))
                page += 1
                if page > self.max_depth:
                    self.log.warning('reached max depth - skipping')
                    break
                url, response = self._requestArtistsPage(idx, page)
            if response:
                self.log.info('no more page for index \'{:s}\''.format(idx))
            else:
                self.log.warning('cannot open URL {:s} - skipping'.format(url))

    def crawl(self):
        self._setUp()
        self._browse()
        self.log.info('crawling completed')
