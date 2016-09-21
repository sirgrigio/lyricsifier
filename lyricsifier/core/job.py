import csv
import logging
import os
import tempfile
from lyricsifier.core.extractor \
    import MetroLyricsExtractor, LyricsComExtractor, \
    LyricsModeExtractor, AZLyricsExtractor
from lyricsifier.core.tagger import LastFMTagger
from lyricsifier.core.worker import ExtractWorker, TagWorker
from lyricsifier.core.utils import csv as csvutils, file


class ExtractJob:

    __extractors__ = [MetroLyricsExtractor(), LyricsComExtractor(),
                      LyricsModeExtractor(), AZLyricsExtractor(), ]

    def __init__(self, fin, fout, processes=1, extractors=__extractors__):
        self.fin = fin
        self.fout = fout
        self.processes = processes
        self.extractors = extractors
        self.tsv_headers = ['trackid', 'lyrics']
        self.log = logging.getLogger(__name__)

    def _setUp(self):
        self.log.info('setting up')
        file.mkdirs(os.path.dirname(self.fout), safe=True)
        with open(self.fout, 'w', encoding='utf8') as tsvout:
            writer = csv.DictWriter(tsvout,
                                    delimiter='\t',
                                    fieldnames=self.tsv_headers)
            writer.writeheader()
        self.log.debug('processes: {:d}'.format(self.processes))
        self.log.debug('extractors: {}'.format(self.extractors))
        self.log.debug('output file: {:s}'.format(self.fout))

    def _createWorkers(self, tmpdir, splits):
        self.log.info('creating workers')
        workers = []
        for i in range(self.processes):
            wid = 'w{:d}'.format(i)
            fout = os.path.join(tmpdir, wid)
            tracks = splits[i]
            workers.append(
                ExtractWorker(
                    wid,
                    tracks,
                    fout,
                    extractors=self.extractors
                )
            )
            self.log.info('worker {} created'.format(wid))
        return workers

    def _merge(self, workers):
        self.log.info('merging output files')
        with open(self.fout, 'a', encoding='utf8') as tsvout:
            writer = csv.DictWriter(tsvout,
                                    delimiter='\t',
                                    fieldnames=self.tsv_headers)
            for worker in workers:
                with open(worker.fout, 'r', encoding='utf8') as tsvin:
                    reader = csv.DictReader(tsvin, delimiter='\t')
                    for row in reader:
                        writer.writerow(
                            {'trackid': row['trackid'],
                             'lyrics': row['lyrics']}
                        )

    def start(self):
        self._setUp()
        splits = csvutils.load(self.fin, splits=self.processes)
        with tempfile.TemporaryDirectory() as tmpdir:
            workers = self._createWorkers(tmpdir, splits)
            self.log.info('starting workers')
            for worker in workers:
                worker.start()
            self.log.info('waiting for workers...')
            for worker in workers:
                worker.join()
            self._merge(workers)
        self.log.info('extract job completed')


class TagJob:

    __taggers__ = [LastFMTagger(api_key='ac5188f22006a4ef88c6b83746b11118'), ]

    def __init__(self, fin, fout, processes=1, taggers=__taggers__):
        self.fin = fin
        self.fout = fout
        self.processes = processes
        self.taggers = taggers
        self.tsv_headers = ['trackid', 'artist', 'title', 'tag']
        self.log = logging.getLogger(__name__)

    def _setUp(self):
        self.log.info('setting up')
        file.mkdirs(os.path.dirname(self.fout), safe=True)
        with open(self.fout, 'w', encoding='utf8') as tsvout:
            writer = csv.DictWriter(tsvout,
                                    delimiter='\t',
                                    fieldnames=self.tsv_headers)
            writer.writeheader()
        self.log.debug('processes: {:d}'.format(self.processes))
        self.log.debug('taggers: {}'.format(self.taggers))
        self.log.debug('output file: {:s}'.format(self.fout))

    def _createWorkers(self, tmpdir, splits):
        self.log.info('creating workers')
        workers = []
        for i in range(self.processes):
            wid = 'w{:d}'.format(i)
            fout = os.path.join(tmpdir, wid)
            tracks = splits[i]
            workers.append(
                TagWorker(
                    wid,
                    tracks,
                    fout,
                    taggers=self.taggers
                )
            )
            self.log.info('worker {} created'.format(wid))
        return workers

    def _merge(self, workers):
        self.log.info('merging output files')
        with open(self.fout, 'a', encoding='utf8') as tsvout:
            writer = csv.DictWriter(tsvout,
                                    delimiter='\t',
                                    fieldnames=self.tsv_headers)
            for worker in workers:
                with open(worker.fout, 'r', encoding='utf8') as tsvin:
                    reader = csv.DictReader(tsvin, delimiter='\t')
                    for row in reader:
                        writer.writerow(
                            {'trackid': row['trackid'],
                             'artist': row['artist'],
                             'title': row['title'],
                             'tag': row['tag']}
                        )

    def start(self):
        self._setUp()
        splits = csvutils.load(self.fin, splits=self.processes)
        with tempfile.TemporaryDirectory() as tmpdir:
            workers = self._createWorkers(tmpdir, splits)
            self.log.info('starting workers')
            for worker in workers:
                worker.start()
            self.log.info('waiting for workers...')
            for worker in workers:
                worker.join()
            self._merge(workers)
        self.log.info('tag job completed')
