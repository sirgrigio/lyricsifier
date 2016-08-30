import csv
import logging
import time
import threading
from lyricsifier.utils import normalization as nutils
from lyricsifier.utils.connection import SOFTConnError, FATALConnError
from unidecode import unidecode


class BaseWorker(threading.Thread):

    def __init__(self, wid):
        threading.Thread.__init__(self, name=wid)
        self.wid = wid
        self.log = logging.getLogger(__name__)

    def _sleep(self, secs):
        self.log.warning(
            'going to sleep for {:d} seconds'.format(secs))
        time.sleep(secs)

    def work(self):
        pass

    def run(self):
        try:
            self.work()
        except Exception as e:
            self.log.error(e)
            raise e


class ExtractWorker(BaseWorker):

    def __init__(self, wid, tracks, fout, extractors, max_delay=500):
        BaseWorker.__init__(self, wid)
        self.tracks = tracks
        self.fout = fout
        self.extractors = extractors
        self.max_delay = max_delay
        self.tsv_headers = ['trackid', 'lyrics']

    def _selectExtractor(self, url):
        for extractor in self.extractors:
            if extractor.canExtractFromURL(url):
                return extractor
        return None

    def _extract(self, url, extractor):
        self.log.info('extracting from {:s} with {}'.format(url, extractor))
        delay = 1
        while delay < self.max_delay:
            try:
                return extractor.extractFromURL(url)
            except SOFTConnError as e:
                self.log.error(e)
                delay *= 2
                self._sleep(delay)
            except FATALConnError as e:
                self.log.error(e)
                return None
        return None

    def work(self):
        with open(self.fout, 'w', encoding='utf8') as tsvout:
            writer = csv.DictWriter(tsvout,
                                    delimiter='\t',
                                    fieldnames=self.tsv_headers)
            writer.writeheader()
            tot = len(self.tracks)
            for i, track in enumerate(self.tracks):
                self.log.info(
                    'track {:d}/{:d} - {}'.format((i + 1), tot, track))
                trackid = track['trackid']
                url = track['url']
                extractor = self._selectExtractor(url)
                if not extractor:
                    self.log.warning(
                        'no extractor suitable for {:s} - skipping'
                        .format(url))
                    continue
                lyrics = self._extract(url, extractor)
                if lyrics:
                    lyrics = nutils.inline(
                        unidecode(nutils.decode(lyrics)), lower=True)
                    self.log.debug(
                        'lyrics normalized - {}'
                        .format(lyrics))
                    self.log.info('writing data to output file')
                    writer.writerow(
                        {'trackid': trackid,
                         'lyrics': lyrics}
                    )
                else:
                    self.log.warning(
                        'cannot extract from {} - skipping'.format(url))
            self.log.info('worker {} finished'.format(self.wid))


class TagWorker(BaseWorker):

    def __init__(self, wid, tracks, fout, taggers, max_delay=500):
        BaseWorker.__init__(self, wid)
        self.tracks = tracks
        self.fout = fout
        self.taggers = taggers
        self.max_delay = max_delay
        self.tsv_headers = ['trackid', 'artist', 'title', 'tag']

    def _tag(self, artist, title):
        self.log.info('getting tag for "{}"-"{}"'.format(artist, title))
        for tagger in self.taggers:
            self.log.info
            delay = 1
            while delay < self.max_delay:
                try:
                    tag = tagger.tag(artist, title)
                    if tag:
                        return tag
                except SOFTConnError as e:
                    self.log.error(e)
                    delay *= 2
                    self._sleep(delay)
                except FATALConnError as e:
                    self.log.error(e)
                    break
        return None

    def work(self):
        with open(self.fout, 'w', encoding='utf8') as tsvout:
            writer = csv.DictWriter(tsvout,
                                    delimiter='\t',
                                    fieldnames=self.tsv_headers)
            writer.writeheader()
            tot = len(self.tracks)
            for i, track in enumerate(self.tracks):
                self.log.info(
                    'track {:d}/{:d} - {}'.format((i + 1), tot, track))
                trackid = track['trackid']
                artist = track['artist']
                title = track['title']
                tag = self._tag(artist, title)
                if tag:
                    self.log.info(
                        'track "{}"-"{}" tagged as {}'
                        .format(artist, title, tag))
                    self.log.info('writing data to output file')
                    writer.writerow(
                        {'trackid': trackid,
                         'artist': artist,
                         'title': title,
                         'tag': tag}
                    )
                else:
                    self.log.warning(
                        'cannot tag "{}"-"{}" - skipping'
                        .format(artist, title))
            self.log.info('worker {} finished'.format(self.wid))
