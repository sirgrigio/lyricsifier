import csv
import logging
import os
import tempfile
from sklearn.feature_selection import SelectKBest, chi2
from lyricsifier.core.classification \
    import Dataset, KMeansAlgorithm, PerceptronAlgorithm, \
    MultinomialNBAlgorithm
from lyricsifier.core.extractor \
    import MetroLyricsExtractor, LyricsComExtractor, \
    LyricsModeExtractor, AZLyricsExtractor
from lyricsifier.core.vectorizer import LyricsVectorizer
from lyricsifier.core.worker import ExtractWorker, TagWorker
from lyricsifier.core.utils import csv as csvutils, file


class ExtractJob:

    __extractors__ = [MetroLyricsExtractor(), LyricsComExtractor(),
                      LyricsModeExtractor(), AZLyricsExtractor(), ]

    def __init__(self, fin, fout, extractors=__extractors__, processes=1):
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

    def __init__(self, fin, fout, taggers, processes=1):
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


class ClusterJob():

    def __init__(self, lyrics_file, tags_file, runs=10):
        self.flyrics = lyrics_file
        self.ftags = tags_file
        self.runs = runs
        self.log = logging.getLogger(__name__)

    def _buildDataset(self):
        data = []
        labels = []
        ftags_rows = csvutils.load(self.ftags)[0]
        tags = {row['trackid']: row['tag'] for row in ftags_rows}
        flyrics_rows = csvutils.load(self.flyrics)[0]
        for row in flyrics_rows:
            trackid = row['trackid']
            lyrics = row['lyrics']
            tag = tags.get(trackid, None)
            if tag:
                data.append(lyrics)
                labels.append(tag)
        return Dataset(data, labels)

    def start(self):
        self.log.info('setting up')
        dataset = self._buildDataset()
        kmc = KMeansAlgorithm(dataset, self.runs)
        kmc.run()
        self.log.info('clustering job completed')


class ClassifyJob():

    def __init__(self, lyrics_file, tags_file, outdir):
        self.flyrics = lyrics_file
        self.ftags = tags_file
        self.outdir = outdir
        self.vectorizer = LyricsVectorizer()
        self.chisquared = SelectKBest(chi2)
        self.log = logging.getLogger(__name__)

    def _buildDataset(self):
        data = []
        labels = []
        ftags_rows = csvutils.load(self.ftags)[0]
        tags = {row['trackid']: row['tag'] for row in ftags_rows}
        flyrics_rows = csvutils.load(self.flyrics)[0]
        for row in flyrics_rows:
            trackid = row['trackid']
            lyrics = row['lyrics']
            tag = tags.get(trackid, None)
            if tag:
                data.append(lyrics)
                labels.append(tag)
        return Dataset(data, labels)

    def _setUp(self):
        self.log.info('setting up')
        file.mkdirs(self.outdir, safe=True)
        dataset = self._buildDataset()
        self.trainset, self.testset = Dataset.split(dataset, 0.8)
        self.trainset.vectorize(self.vectorizer)
        self.testset.vectorize(self.vectorizer, fit=False)

    def start(self):
        self._setUp()
        features = self.trainset.data.shape[1]
        for k in ['all', features // 2, features // 4,
                  features // 8, features // 16]:
            trainset = Dataset(self.trainset.data, self.trainset.target)
            testset = Dataset(self.testset.data, self.testset.target)
            if k != 'all':
                trainset.selectBestFeatures(self.chisquared, k)
                testset.selectBestFeatures(self.chisquared, k, fit=False)
            algorithms = [
                PerceptronAlgorithm(trainset, testset),
                MultinomialNBAlgorithm(trainset, testset)
            ]
            for alg in algorithms:
                self.log.info(
                    'running {:s} with {} features'.format(alg.name, k))
                report = alg.run()
                filename = '{:s}_{}.txt'.format(alg.name, k)
                with open(
                    os.path.join(self.outdir, filename),
                    'w', encoding='utf8'
                ) as fout:
                    print(report, file=fout)
                    self.log.info('report written to {}'.format(filename))
        self.log.info('clustering job completed')
