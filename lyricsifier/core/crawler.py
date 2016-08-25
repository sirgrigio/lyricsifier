import csv
import logging
import os
import re
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
from string import ascii_lowercase


class MetroLyricsCrawler:

    def _createOutDirIfNotExists(self, outdir):
        if not os.path.exists(outdir):
            self.log.warning('output directory does not exist - creating it')
            os.makedirs(outdir)

    def _writeTSVHeader(self):
        with open(self.fout, 'w', encoding='utf8') as tsvout:
            self.log.info('creating output tsv file')
            writer = csv.DictWriter(tsvout,
                                    delimiter='\t',
                                    fieldnames=self.tsv_headers)
            writer.writeheader()

    def _bulkWriteTSVRows(self, rows):
        with open(self.fout, 'a', encoding='utf8') as tsvout:
            self.log.info('writing rows to file {:s}'.format(self.fout))
            writer = csv.DictWriter(tsvout,
                                    delimiter='\t',
                                    fieldnames=self.tsv_headers)
            writer.writerows(rows)

    def __init__(self, outdir):
        self.base_url = 'http://www.metrolyrics.com'
        self.artists_index = [1] + list(ascii_lowercase)
        self.artists_page_pattern = self.base_url + '/artists-{:s}-{:d}.html'
        self.fout = os.path.join(outdir, 'lyrics.txt')
        self.tsv_headers = ['url', 'artist', 'title']
        self.log = logging.getLogger(__name__)
        self._createOutDirIfNotExists(outdir)
        self._writeTSVHeader()

    def _requestArtistsPage(self, idx, page):
        url = self.artists_page_pattern.format(idx, page)
        self.log.info('requesting URL {:s}'.format(url))
        request = urllib.request.Request(url)
        return url, urllib.request.urlopen(request)

    def _requestSongsPage(self, pattern, page):
        url = pattern.format(page)
        self.log.info('requesting URL {:s}'.format(url))
        request = urllib.request.Request(url)
        return url, urllib.request.urlopen(request)

    def _extractArtistName(self, a_elem):
        text = a_elem.get_text().encode('utf8')
        name = re.sub(
            b' Lyrics$',
            b'',
            text.rstrip([b'\n', b'\r', b'\s', b'\t'])
        )
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
        name = re.sub(
            b' Lyrics$',
            b'',
            text.rstrip([b'\n', b'\r', b'\s', b'\t'])
        )
        self.log.debug(
            'song title {} extracted from {:s}'.format(
                name.decode('utf8'), a_elem.prettify()))
        return name

    def _parseSongsTable(self, artist, table):
        self.log.info('parsing songs table')
        output_rows = []
        for row in table.tbody.findAll('tr'):
            song_a = row.find('td', class_=None).find_next('a', href=True)
            title = self._extractSongTitle(song_a)
            lyrics_url = song_a['href']
            output_rows.append(
                {'url': lyrics_url,
                 'artist': artist,
                 'title': title}
            )
            self.log.info('new lyrics URL crawled - {:s}'.format(lyrics_url))
        self._bulkWriteTSVRows(output_rows)

    def _parseArtistTable(self, table):
        self.log.info('parsing artists table')
        for row in table.tbody.findAll('tr'):
            artist_a = row.find('td').find_next('a', href=True)
            artist = self._extractArtistName(artist_a)
            songs_pattern = self._extractArtistSongsURLPattern(artist_a)
            s_page = 1
            url, response = self._requestSongsPage(songs_pattern, s_page)
            while url == response.geturl():
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table', class_='songs-table-compact')
                if table:
                    self._parseSongsTable(artist, table)
                else:
                    self.log.warning(
                        'cannot crawl from {:s} - skipping'.format(url))

    def crawl(self):
        for idx in self.artists_index:
            self.log.info('crawling index {:s}'.format(idx))
            a_page = 1
            url, response = self._requestArtistsPage(idx, a_page)
            while url == response.geturl():
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find('table', class_='songs-table')
                if table:
                    self._parseArtistTable(table)
                else:
                    self.log.warning(
                        'cannot crawl from {:s} - skipping'.format(url))
                url, response = self._requestArtistsPage(idx, ++a_page)
            self.log.info('no more page for index {:s}'.format(idx))
