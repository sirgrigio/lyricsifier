import logging
import math
import numpy
import random
import time
from abc import ABC, abstractmethod
from sklearn import metrics
from sklearn.cluster import AffinityPropagation, KMeans, DBSCAN
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import Perceptron
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import MLPClassifier
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline


class Dataset():

    def __init__(self, data, labels, name='dataset'):
        self.name = name
        self.data = data
        self.target = labels

    def vectorize(dataset, vectorizer, fit=True):
        log = logging.getLogger(__name__)
        log.info('preprocessing {:s}'.format(dataset.name))
        dataset.data = vectorizer.vectorize(dataset.data, fit=fit)

    def split(dataset, percentage):
        log = logging.getLogger(__name__)
        log.info('splitting dataset')
        total_size = len(dataset.data)
        log.info('{:d} elements in orginal dataset'.format(total_size))
        testset_size = math.ceil(total_size * (1 - percentage))
        testset_ids = set(random.sample(range(total_size), testset_size))
        testset_data = [dataset.data[i] for i in testset_ids]
        testset_target = [dataset.target[i] for i in testset_ids]
        log.info('extracted testset of size {:d}'.format(len(testset_ids)))
        dataset_ids = set(range(total_size)) - testset_ids
        dataset_data = [dataset.data[i] for i in dataset_ids]
        dataset_target = [dataset.target[i] for i in dataset_ids]
        log.info('extracted trainset of size {:d}'.format(len(dataset_ids)))
        return Dataset(dataset_data, dataset_target, 'trainset'), \
            Dataset(testset_data, testset_target, 'testset')


class LearningAlgorithm(ABC):

    def __init__(self):
        self.log = logging.getLogger(__name__)

    @abstractmethod
    def run(self):
        pass


class UnsupervisedAlgorithm(LearningAlgorithm):

    def __init__(self, name, algorithm, dataset):
        LearningAlgorithm.__init__(self)
        self.name = name
        self.algorithm = algorithm
        self.dataset = dataset

    def run(self):
        X = self.dataset
        self.log.info('{} clustering started'.format(self.name))
        self.algorithm.fit(X.data)
        self.log.info(
            '{} clustering completed - computing scores'.format(self.name))
        homogeneity = metrics.homogeneity_score(
            X.target, self.algorithm.labels_)
        completeness = metrics.completeness_score(
            X.target, self.algorithm.labels_)
        self.log.info(
            '{} homogeneity score: {:.3f}'.format(self.name, homogeneity))
        self.log.info(
            '{} completeness score: {:.3f}'.format(self.name, completeness))


class KMeansAlgorithm(UnsupervisedAlgorithm):

    def __init__(self, dataset, jobs, runs=10):
        UnsupervisedAlgorithm.__init__(
            self,
            'k-means',
            KMeans(
                n_clusters=numpy.unique(dataset.target).shape[0],
                n_init=runs,
                max_iter=100,
                n_jobs=jobs
            ),
            dataset
        )


class AffinityPropagationAlgorithm(UnsupervisedAlgorithm):

    def __init__(self, dataset):
        UnsupervisedAlgorithm.__init__(
            self,
            'affinity propagation',
            AffinityPropagation(),
            dataset
        )


class DBScanAlgorithm(UnsupervisedAlgorithm):

    def __init__(self, dataset, jobs):
        UnsupervisedAlgorithm.__init__(
            self,
            'dbscan',
            DBSCAN(
                eps=0.3,
                min_samples=5,
                n_jobs=jobs
            ),
            dataset
        )


class SupervisedAlgorithm(LearningAlgorithm):

    def __init__(self, name, algorithm, trainset, testset,
                 feature_selection=False):
        LearningAlgorithm.__init__(self)
        self.name = (name if not feature_selection
                     else name + '_feature-selection')
        self.algorithm = algorithm
        if feature_selection:
            sel = SelectFromModel(
                LinearSVC(C=0.01, penalty='l1', dual=False)
            )
            self.algorithm = Pipeline(
                [('feature_selection', sel), ('classification', algorithm)]
            )
        self.trainset = trainset
        self.testset = testset

    def run(self):
        self.log.info('{:s} started'.format(self.name))
        self.log.info('running {:s} on trainset'.format(self.name))
        t1 = time.time()
        self.algorithm.fit(self.trainset.data, self.trainset.target)
        train_time = time.time() - t1
        self.log.info(
            '{:s} training completed in {:.3f}s'.format(self.name, train_time))
        self.log.info('running {:s} on testset'.format(self.name))
        t2 = time.time()
        predictions = self.algorithm.predict(self.testset.data)
        test_time = time.time() - t2
        self.log.info(
            '{:s} test completed in {:.3f}s'.format(self.name, test_time))
        accuracy = metrics.accuracy_score(self.testset.target, predictions)
        self.log.info(
            '{:s} accuracy score: {:.3f}'.format(self.name, accuracy))
        f1_score = metrics.f1_score(
            self.testset.target, predictions, average='weighted')
        self.log.info(
            '{:s} weighted f1 score: {:.3f}'.format(self.name, f1_score))
        return metrics.classification_report(self.testset.target, predictions)


class PerceptronAlgorithm(SupervisedAlgorithm):

    def __init__(self, trainset, testset, feature_selection=False):
        SupervisedAlgorithm.__init__(
            self,
            'perceptron',
            Perceptron(),
            trainset,
            testset,
            feature_selection
        )


class MultinomialNBAlgorithm(SupervisedAlgorithm):

    def __init__(self, trainset, testset, feature_selection=False):
        SupervisedAlgorithm.__init__(
            self,
            'multinomial-nb',
            MultinomialNB(),
            trainset,
            testset,
            feature_selection
        )


class RandomForestAlgorithm(SupervisedAlgorithm):

    def __init__(self, trainset, testset, feature_selection=False):
        SupervisedAlgorithm.__init__(
            self,
            'random-forest',
            RandomForestClassifier(),
            trainset,
            testset,
            feature_selection
        )


class SVMAlgorithm(SupervisedAlgorithm):

    def __init__(self, trainset, testset, feature_selection=False):
        SupervisedAlgorithm.__init__(
            self,
            'svm',
            LinearSVC(),
            trainset,
            testset,
            feature_selection
        )


class MLPAlgorithm(SupervisedAlgorithm):

    def __init__(self, trainset, testset):
        SupervisedAlgorithm.__init__(
            self,
            'mlp',
            MLPClassifier(),
            trainset,
            testset,
            feature_selection=True
        )
