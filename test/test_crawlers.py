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
        self.crawlers = [LyricsComCrawler()]

    def test_fail(self):
        print
        artist = 'NoArtistWithThisName' 
        title = 'NoSongWithThisTitle'
        for crawler in self.crawlers:
            self.assertIsNone(crawler.crawl(artist, title))

    def test_ok(self):
        print
        artist = 'Britney Spears'
        title = 'Make Me... (feat. G-Eazy)'
        for crawler in self.crawlers:
            self.assertIsNotNone(crawler.crawl(artist, title))


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
                print '\n\n\n\n\n%-5d\t%s\n\n\n\n\n' % (i, crawler)
                self.assertIsNotNone(crawler.crawl(artist, song))

if __name__ == '__main__':
    unittest.main()
