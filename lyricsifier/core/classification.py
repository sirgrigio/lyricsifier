import logging
import math
import numpy
import random
from abc import ABC, abstractmethod
from sklearn import metrics
from sklearn.cluster import AffinityPropagation, KMeans, DBSCAN
from sklearn.ensemble import \
    BaggingClassifier, RandomForestClassifier
from sklearn.linear_model import Perceptron
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC


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
                n_jobs=jobs
            ),
            dataset
        )


class SupervisedAlgorithm(LearningAlgorithm):

    def __init__(self, name, algorithm, trainset, testset):
        LearningAlgorithm.__init__(self)
        self.name = name
        self.algorithm = algorithm
        self.trainset = trainset
        self.testset = testset

    def run(self):
        self.log.info('{:s} started'.format(self.name))
        self.log.info('running {:s} on trainset'.format(self.name))
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
            Perceptron(
                n_iter=50,
            ),
            trainset,
            testset
        )


class MultinomialNBAlgorithm(SupervisedAlgorithm):

    def __init__(self, trainset, testset):
        SupervisedAlgorithm.__init__(
            self,
            'multinomialnb',
            MultinomialNB(
                alpha=0.01
            ),
            trainset,
            testset
        )


class RandomForestAlgorithm(SupervisedAlgorithm):

    def __init__(self, trainset, testset, jobs):
        SupervisedAlgorithm.__init__(
            self,
            'randomforest',
            RandomForestClassifier(
                n_jobs=jobs
            ),
            trainset,
            testset
        )


class SVMAlgorithm(SupervisedAlgorithm):

    def __init__(self, trainset, testset, jobs):
        SupervisedAlgorithm.__init__(
            self,
            'svm',
            OneVsRestClassifier(
                BaggingClassifier(
                    SVC(
                        tol=0.05
                    ),
                    max_samples=0.1,
                    n_jobs=jobs
                )
            ),
            trainset,
            testset
        )


class MLPAlgorithm(SupervisedAlgorithm):

    def __init__(self, trainset, testset):
        SupervisedAlgorithm.__init__(
            self,
            'mlp',
            MLPClassifier(
                solver='adam',
                alpha=1e-5,
                hidden_layer_sizes=(5, 2),
                random_state=1,
            ),
            trainset,
            testset
        )
