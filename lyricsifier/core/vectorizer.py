import logging
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer


class LyricsTokenizer:

    def __init__(self):
        self.stopwords = stopwords.words('english')
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.stemmer = PorterStemmer()

    def __call__(self, doc):
        return [self.stemmer.stem(w)
                for w in self.tokenizer.tokenize(doc)
                if len(w) > 1 and w not in self.stopwords]


class LyricsVectorizer:

    def __init__(self, min_df=1, max_df=0.7, tokenizer=LyricsTokenizer()):
        self.vectorizer = TfidfVectorizer(
            min_df=min_df,
            max_df=max_df,
            tokenizer=tokenizer,
            sublinear_tf=True
        )
        self.log = logging.getLogger(__name__)

    def vectorize(self, corpus):
        self.log.info('vectorizing {:d} documents'.format(len(corpus)))
        self.log.info(
            'vectorization started - this may require several minutes to complete')
        corpus_matrix = self.vectorizer.fit_transform(corpus)
        self.log.info(
            'vectorization completed - {:d} features and {:d} samples'
            .format(corpus_matrix.shape[0], corpus_matrix.shape[1]))
        return corpus_matrix
