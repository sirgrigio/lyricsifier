import csv
import logging
import os
import re
import time
import threading
import urllib.error
from lyricsifier.core.extractor \
    import MetroLyricsExtractor, LyricsComExtractor, \
    LyricsModeExtractor, AZLyricsExtractor
from unidecode import unidecode


class ExtractWorker(threading.Thread):

    def __sleep(self, secs):
        self.log.warning(
            'going to sleep for {:d} seconds'.format(secs))
        time.sleep(secs)

    def __init__(self, wid, tracks, fout, extractors, max_delay=500):
        threading.Thread.__init__(self, name=wid)
        self.wid = wid
        self.tracks = tracks
        self.fout = fout
        self.extractors = extractors
        self.max_delay = max_delay
        self.tsv_headers = ['url', 'artist', 'title', 'lyrics']
        self.log = logging.getLogger(__name__)
        self.log.info('worker {} initialized')

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

    def _extract(self, url, extractor):
        self.log.info('extracting from {:s} with {}'.format(url, extractor))
        delay = 1
        while delay < self.max_delay:
            try:
                return extractor.extractFromURL(url)
            except urllib.error.HTTPError as e:
                self.log.error(e)
                if 400 <= e.code < 500 and e.code != 408:
                    return None
                delay *= 2
                self.__sleep(delay)
            except urllib.error.URLError as e:
                self.log.error(e)
                delay *= 2
                self.__sleep(delay)
        return None

    def run(self):
        try:
            with open(self.fout, 'w', encoding='utf8') as tsvout:
                writer = csv.DictWriter(tsvout,
                                        delimiter='\t',
                                        fieldnames=self.tsv_headers)
                writer.writeheader()
                tot = len(self.tracks)
                for i, track in enumerate(self.tracks):
                    self.log.info('track {:d}/{:d} - {}'.format(i, tot, track))
                    url = track['url']
                    artist = track['artist']
                    title = track['title']
                    extractor = self._selectExtractor(url)
                    if not extractor:
                        self.log.warning(
                            'no extractor suitable for {:s} - skipping'
                            .format(url))
                        continue
                    lyrics = self._extract(url, extractor)
                    if lyrics:
                        lyrics = self._normalize(lyrics.decode('utf8'))
                        self.log.debug(
                            'lyrics normalized - {}'
                            .format(lyrics.encode('utf8')))
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
                self.log.info('worker {} finished'.format(self.wid))
        except Exception as e:
            self.log.error(e)
            raise e


class ExtractJob:

    __extractors__ = [MetroLyricsExtractor(), LyricsComExtractor(),
                      LyricsModeExtractor(), AZLyricsExtractor(), ]

    def __createWorkersDirIfNotExists(self):
        if not os.path.exists(self.workersdir):
            self.log.warning(
                'workers directory {:s} does not exist - creating it'.format(
                    self.workersdir))
            os.makedirs(self.workersdir)

    def __init__(self, fin, fout, threads=1, extractors=__extractors__):
        self.fin = fin
        self.fout = fout
        self.workersdir = os.path.join(os.path.dirname(self.fout), 'workers')
        self.threads = threads
        self.extractors = extractors
        self.tsv_headers = ['url', 'artist', 'title', 'lyrics']
        self.log = logging.getLogger(__name__)
        self.log.info(
            'extract job initialized - fin {:s} - fout {:s} - workers {:d}'
            .format(self.fin, self.fout, self.threads))
        self.log.info('')
        self.__createWorkersDirIfNotExists()

    def _splitInput(self):
        self.log.info('splitting input for workers')
        splits = []
        for i in range(self.threads):
            splits.append([])
        with open(self.fin, 'r', encoding='utf8') as tsvin:
            reader = csv.DictReader(tsvin, delimiter='\t')
            for i, row in enumerate(reader):
                widx = i % self.threads
                splits[widx].append(
                    {'url': row['url'],
                     'artist': row['artist'],
                     'title': row['title']}
                )
        return splits

    def _initWorkers(self, splits):
        self.log.info('creating workers')
        workers = []
        for i in range(self.threads):
            wid = 'w{:d}'.format(i)
            workerout = os.path.join(self.workersdir, wid)
            self.log.info('worker {} - out-file {}'.format(wid, workerout))
            tracks = splits[i]
            workers.append(
                ExtractWorker(
                    wid,
                    tracks,
                    workerout,
                    extractors=self.extractors
                )
            )
        return workers

    def _mergeOutFiles(self, workers):
        self.log.info('merging output files')
        with open(self.fout, 'w', encoding='utf8') as tsvout:
            writer = csv.DictWriter(tsvout,
                                    delimiter='\t',
                                    fieldnames=self.tsv_headers)
            writer.writeheader()
            for worker in workers:
                with open(worker.fout, 'r', encoding='utf8') as tsvin:
                    reader = csv.DictReader(tsvin, delimiter='\t')
                    for row in reader:
                        writer.writerow(
                            {'url': row['url'],
                             'artist': row['artist'],
                             'title': row['title'],
                             'lyrics': row['lyrics']}
                        )

    def start(self):
        splits = self._splitInput()
        workers = self._initWorkers(splits)
        self.log.info('starting workers')
        for worker in workers:
            worker.start()
        self.log.info('waiting for workers...')
        for worker in workers:
            worker.join()
        self._mergeOutFiles(workers)
        self.log.info('extract job completed')
