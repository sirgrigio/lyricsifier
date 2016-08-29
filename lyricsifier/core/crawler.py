import csv
import logging
import os
import re
import time
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
from string import ascii_lowercase
from lyricsifier.utils import file


class MetroLyricsCrawler:

    def __writeTSVHeader(self):
        with open(self.fout, 'w', encoding='utf8') as tsvout:
            self.log.info('creating output tsv file')
            writer = csv.DictWriter(tsvout,
                                    delimiter='\t',
                                    fieldnames=self.tsv_headers)
            writer.writeheader()

    def __bulkWriteTSVRows(self, rows):
        with open(self.fout, 'a', encoding='utf8') as tsvout:
            self.log.info('writing rows to file {:s}'.format(self.fout))
            writer = csv.DictWriter(tsvout,
                                    delimiter='\t',
                                    fieldnames=self.tsv_headers)
            writer.writerows(rows)

    def __rreplace(self, s, old, new, occurrence=1):
        li = s.rsplit(old, occurrence)
        return new.join(li)

    def __sleep(self, secs):
        self.log.warning(
            'going to sleep for {:d} seconds'.format(secs))
        time.sleep(secs)

    def __open(self, request):
        delay = 1
        while delay < self.max_delay:
            try:
                return urllib.request.urlopen(request)
            except urllib.error.HTTPError as e:
                self.log.error(e)
                if 400 <= e.code < 500:
                    return None
                delay *= 2
                self.__sleep(delay)
            except urllib.error.URLError as e:
                self.log.error(e)
                delay *= 2
                self.__sleep(delay)
            except Exception as e:
                self.log.error(e)
                return None
        return None

    def __init__(self, fout, max_delay, max_depth=100):
        self.base_url = 'http://www.metrolyrics.com'
        self.artists_index = ['1'] + list(ascii_lowercase)
        self.artists_page_pattern = self.base_url + '/artists-{:s}-{:d}.html'
        self.fout = os.path.abspath(fout)
        self.max_delay = max_delay
        self.max_depth = max_depth
        self.tsv_headers = ['url', 'artist', 'title']
        self.log = logging.getLogger(__name__)
        file.mkdirs(os.path.dirname(self.fout), safe=True)
        self.__writeTSVHeader()
        self.log.info(
            'crawler initialized with output file {:s} and max delay {:d}'
            .format(self.fout, self.max_delay))

    def _requestArtistsPage(self, idx, page):
        url = self.artists_page_pattern.format(str(idx), page)
        self.log.info('requesting URL {:s}'.format(url))
        request = urllib.request.Request(url)
        return url, self.__open(request)

    def _requestSongsPage(self, pattern, page):
        url = pattern.format(page)
        self.log.info('requesting URL {:s}'.format(url))
        request = urllib.request.Request(url)
        return url, self.__open(request)

    def _extractArtistName(self, a_elem):
        text = a_elem.get_text().encode('utf8')
        name = self.__rreplace(text, b' Lyrics', b'').strip(b'\n\r\s\t')
        self.log.debug(
            'artist name {} extracted from {:s}'.format(
                name.decode('utf8'), a_elem.prettify()))
        return name

    def _extractArtistSongsPagePattern(self, a_elem):
        href = a_elem['href']
        pattern = re.sub('-lyrics.html$', '-alpage-{}.html', href)
        self.log.debug(
            'songs page pattern {:s} extracted from {:s}'.format(
                pattern, a_elem.prettify()))
        return pattern

    def _extractSongTitle(self, a_elem):
        text = a_elem.get_text().encode('utf8')
        title = self.__rreplace(text, b' Lyrics', b'').strip(b'\n\r\s\t')
        self.log.debug(
            'song title {} extracted from {:s}'.format(
                title.decode('utf8'), a_elem.prettify()))
        return title

    def _parseSongsTable(self, artist, table):
        self.log.info('parsing songs table')
        output_rows = []
        for row in table.tbody.findAll('tr'):
            song_a = row.find('td', class_=None).find_next('a', href=True)
            title = self._extractSongTitle(song_a)
            lyrics_url = song_a['href']
            output_rows.append(
                {'url': lyrics_url,
                 'artist': artist.decode('utf8'),
                 'title': title.decode('utf8')}
            )
            self.log.info('new lyrics URL crawled - {:s}'.format(lyrics_url))
        self.__bulkWriteTSVRows(output_rows)

    def _parseArtistTable(self, table):
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
                        artist.decode('utf8')))
            else:
                self.log.warning('cannot open URL {:s} - skipping'.format(url))

    def crawl(self):
        for idx in self.artists_index:
            self.log.info('crawling index \'{:s}\''.format(idx))
            page = 1
            url, response = self._requestArtistsPage(idx, page)
            while response and url == response.geturl():
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table', class_='songs-table')
                if table:
                    self._parseArtistTable(table)
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
        self.log.info('crawling completed')
