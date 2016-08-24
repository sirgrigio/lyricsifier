import logging
import lyricsifier
import unittest
from lyricsifier.core.crawler import LyricsComCrawler, LyricsModeCrawler


class TestCrawlers(unittest.TestCase):

    def _configureLogging(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-38s %(levelname)-8s %(message)s',)

    def setUp(self):
        self._configureLogging()
        self.crawlers = [LyricsComCrawler(), LyricsModeCrawler()]

    def testFail(self):
        print
        artist = 'NoArtistWithThisName' 
        title = 'NoSongWithThisTitle'
        for crawler in self.crawlers:
            self.assertIsNone(crawler.crawl(artist, title))

    def testOkPlain(self):
        print
        artist = 'Alicia Keys'
        title = 'No One'
        for crawler in self.crawlers:
            self.assertIsNotNone(crawler.crawl(artist, title))

    def testOkSpecial(self):
        print
        tracks = [{'artist': 'AC/DC', 'title': 'T.N.T.'},
                  {'artist': 'Justin Timberlake', 'title': 'Can\'t stop the feeling!'}]
        for crawler in self.crawlers:
            for track in tracks:
                self.assertIsNotNone(crawler.crawl(track['artist'], track['title']))


class TestCrawlersLimit(unittest.TestCase):

    def _configureLogging(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-38s %(levelname)-8s %(message)s',)

    def setUp(self):
        self._configureLogging()
        self.crawlers = [LyricsComCrawler()]

    def test_limit(self):
        print
        artist = 'Alicia Keys'
        song = 'No One'
        for i in range(10000):
            for crawler in self.crawlers:
                print('\n\n\n\n\n{:-5d}\t{}\n\n\n\n\n'.format(i, crawler))
                self.assertIsNotNone(crawler.crawl(artist, song))

if __name__ == '__main__':
    unittest.main()
