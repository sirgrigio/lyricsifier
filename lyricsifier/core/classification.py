import logging
import math
import numpy
import random
from abc import ABC, abstractmethod
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.linear_model import Perceptron
from sklearn.naive_bayes import MultinomialNB


class Dataset():

    def __init__(self, data, labels, name='dataset'):
        self.name = name
        self.data = data
        self.target = labels
        self.log = logging.getLogger(__name__)

    def vectorize(self, vectorizer, fit=True):
        self.log.info('preprocessing {:s}'.format(self.name))
        self.data = vectorizer.vectorize(self.data, fit=fit)

    def selectBestFeatures(self, selector, k, fit=True):
        self.log.info('extracting best {} features'.format(k))
        self.log.info('using dataset to fit: {}'.format(fit))
        self.data = selector.fit_transform(self.data, self.target) if fit else selector.transform(self.data)

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


class KMeansAlgorithm(LearningAlgorithm):

    def __init__(self, dataset, runs=10):
        LearningAlgorithm.__init__(self)
        self.km = KMeans(
            n_clusters=numpy.unique(dataset.target).shape[0],
            n_init=runs,
            verbose=True
        )

    def run(self):
        X = self.dataset
        X.vectorize(self.vectorizer)
        self.log.info('starting k-means clustering')
        self.km.fit(X.data)
        self.log.info('k-means clustering completed - computing scores')
        homogeneity = metrics.homogeneity_score(X.target, self.km.labels_)
        completeness = metrics.completeness_score(X.target, self.km.labels_)
        self.log.info('homogeneity score: {:.3f}'.format(homogeneity))
        self.log.info('completeness score: {:.3f}'.format(completeness))


class SupervisedAlgorithm(LearningAlgorithm):

    def __init__(self, name, algorithm, trainset, testset):
        LearningAlgorithm.__init__(self)
        self.name = name
        self.algorithm = algorithm
        self.trainset = trainset
        self.testset = testset

    def run(self):
        self.log.info('starting {:s}'.format(self.name))
        self.algorithm.fit(self.trainset.data, self.trainset.target)
        self.log.info('{:s} training completed'.format(self.name))
        self.log.info('running {:s} on testset'.format(self.name))
        predictions = self.algorithm.predict(self.testset.data)
        accuracy = metrics.accuracy_score(self.testset.target, predictions)
        self.log.info(
            '{:s} accuracy score: {:.3f}'.format(self.name, accuracy))
        return metrics.classification_report(self.testset.target, predictions)


class PerceptronAlgorithm(SupervisedAlgorithm):

    def __init__(self, trainset, testset):
        SupervisedAlgorithm.__init__(
            self,
            'perceptron',
            Perceptron(n_iter=50),
            trainset,
            testset
        )


class MultinomialNBAlgorithm(SupervisedAlgorithm):

    def __init__(self, trainset, testset):
        SupervisedAlgorithm.__init__(
            self,
            'multinomialnb',
            MultinomialNB(alpha=0.01),
            trainset,
            testset
        )