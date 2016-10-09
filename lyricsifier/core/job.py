
import csv
import logging
import os
import pickle
import tempfile
from lyricsifier.core.classification \
    import Dataset, KMeansAlgorithm, DBScanAlgorithm, AffinityPropagation, \
    PerceptronAlgorithm, MultinomialNBAlgorithm, RandomForestAlgorithm, \
    SVMAlgorithm, MLPAlgorithm
from lyricsifier.core.extractor \
    import MetroLyricsExtractor, LyricsComExtractor, \
    LyricsModeExtractor, AZLyricsExtractor
from lyricsifier.core.vectorizer import LyricsVectorizer
from lyricsifier.core.worker import ExtractWorker, TagWorker
from lyricsifier.core.utils import csv as csvutils, file  # , plot


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


class VectorizeJob():

    def __init__(self, lyrics_file, tags_file, outdir, split=False):
        self.flyrics = lyrics_file
        self.ftags = tags_file
        self.outdir = outdir
        self.split = split
        self.vectorizer = LyricsVectorizer()
        self.log = logging.getLogger(__name__)

    def _setUp(self):
        self.log.info('setting up')
        file.mkdirs(self.outdir, safe=True)
        self.log.info('creating trainset and testset: {}'.format(self.split))

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

    def _dump(self, dataset):
        filename = os.path.join(self.outdir, dataset.name + '.obj')
        self.log.info('dumping {}'.format(dataset.name))
        with open(filename, 'wb') as fobj:
            pickle.dump(dataset, fobj)
        self.log.info('{} dumped to file {}'.format(dataset.name, filename))

    def start(self):
        self._setUp()
        dataset = self._buildDataset()
        self.log.info('dataset loaded')
        if self.split:
            trainset, testset = Dataset.split(dataset, 0.8)
            Dataset.vectorize(trainset, self.vectorizer)
            Dataset.vectorize(testset, self.vectorizer, fit=False)
            self._dump(trainset)
            self._dump(testset)
        else:
            Dataset.vectorize(dataset, self.vectorizer)
            self._dump(dataset)
        self.log.info('vectorize job completed')


class ClusterJob():

    def __init__(self, dataset_file, processes=1):
        self.fdataset = dataset_file
        self.processes = processes
        self.vectorizer = LyricsVectorizer()
        self.log = logging.getLogger(__name__)

    def _loadDataset(self):
        self.log.info(
            'loading dataset from dump file {}'.format(self.fdataset))
        with open(self.fdataset, 'rb') as du:
            return pickle.load(du)

    def start(self):
        self.log.info('setting up')
        dataset = self._loadDataset()
        self.log.info('dataset loaded')
        algorithms = [
            KMeansAlgorithm(dataset, self.processes),
            AffinityPropagation(dataset),
            DBScanAlgorithm(dataset, self.processes)
        ]
        for alg in algorithms:
            alg.run()
        self.log.info('clustering job completed')


class ClassifyJob():

    def __init__(self, trainset_file, testset_file, outdir):
        self.ftrainset = trainset_file
        self.ftestset = testset_file
        self.outdir = outdir
        self.log = logging.getLogger(__name__)

    def _setUp(self):
        self.log.info('setting up')
        file.mkdirs(self.outdir, safe=True)

    def _loadDataset(self, file):
        self.log.info('loading dataset from dump file {}'.format(file))
        with open(file, 'rb') as du:
            return pickle.load(du)

    def start(self):
        self._setUp()
        trainset = self._loadDataset(self.ftrainset)
        testset = self._loadDataset(self.ftestset)
        algorithms = [
            PerceptronAlgorithm(trainset, testset),
            MultinomialNBAlgorithm(trainset, testset),
            RandomForestAlgorithm(trainset, testset, feature_selection=True),
            SVMAlgorithm(trainset, testset),
            MLPAlgorithm(trainset, testset),
        ]
        for alg in algorithms:
            self.log.info('running {:s}'.format(alg.name))
            report = alg.run()
            filename = '{:s}.txt'.format(alg.name)
            with open(
                os.path.join(self.outdir, filename),
                'w', encoding='utf8'
            ) as fout:
                print(report, file=fout)
                self.log.info('report written to {}'.format(filename))
        self.log.info('classify job completed')
