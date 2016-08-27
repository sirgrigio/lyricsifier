import csv
import logging
import re
import urllib.error
from lyricsifier.core.extractor \
    import MetroLyricsExtractor, LyricsComExtractor, \
    LyricsModeExtractor, AZLyricsExtractor
from unidecode import unidecode


class ExtractJob:

    __extractor__ = [MetroLyricsExtractor(), LyricsComExtractor(),
                     LyricsModeExtractor(), AZLyricsExtractor(), ]

    def __init__(self, fin, fout, extractors=__extractor__):
        self.fin = fin
        self.fout = fout
        self.extractors = extractors
        self.tsv_headers = ['url', 'artist', 'title', 'lyrics']
        self.log = logging.getLogger(__name__)
        self.log.info(
            'extract job initialized with input file {:s} and output file {:s}'
            .format(fin, fout))

    def _normalize(self, string):
        s = unidecode(string)
        s = re.sub('[\n\r\t]', ' ', s)
        s = re.sub(' +', ' ', s)
        return s.strip().lower()

    def _selectExtractor(self, url):
        for extractor in self.extractors:
            if extractor.canExtractFromURL(url):
                return extractor
        return None

    def run(self):
        with open(self.fin, 'r', encoding='utf8') as tsvin, open(self.fout, 'w', encoding='utf8') as tsvout:
            writer = csv.DictWriter(tsvout,
                                    delimiter='\t',
                                    fieldnames=self.tsv_headers)
            writer.writeheader()
            reader = csv.DictReader(tsvin, delimiter='\t')
            for i, row in enumerate(reader):
                self.log.info('row {:d} - {}'.format(i, row))
                url = row['url']
                artist = row['artist']
                title = row['title']
                extractor = self._selectExtractor(url)
                if not extractor:
                    self.log.warning(
                        'no extractor suitable for {:s} - skipping'
                        .format(url))
                    continue
                self.log.info(
                    'extracting from {:s} with {}'.format(url, extractor))
                lyrics = None
                try:
                    lyrics = extractor.extractFromURL(url).decode('utf8')
                except urllib.error.URLError as e:
                    self.log.error(e)
                if lyrics:
                    lyrics = self._normalize(lyrics)
                    self.log.debug('lyrics normalized - {:s}'.format(lyrics))
                    self.log.info('writing data to output file')
                    writer.writerow(
                        {'url': url,
                         'artist': artist,
                         'title': title,
                         'lyrics': lyrics}
                    )
                else:
                    self.log.warning(
                        'cannot extract from {} - skipping'.format(url))
            self.log.info('extract job completed')
