import unittest
from lyricsifier.utils import logging
from lyricsifier.core.extractor \
    import MetroLyricsExtractor, LyricsComExtractor, \
    LyricsModeExtractor, AZLyricsExtractor, URLError


class TestExtractors(unittest.TestCase):

    def setUp(self):
        logging.loadcfg(default_path='logging_test.json')

    def testMetroLyrics(self):
        print()
        extractor = MetroLyricsExtractor()
        base_url = 'http://www.metrolyrics.com'
        ok_urls = [
            base_url + '/no-one-lyrics-alicia-keys.html',
            base_url + '/tnt-lyrics-acdc.html',
            base_url + '/cant-stop-the-feeling-lyrics-justin-timberlake.html',
            base_url + '/because-the-night-lyrics-10000-maniacs.html',
        ]
        fail_urls = [
            'http://anothersite.com/no-one-lyrics-alicia-keys.html',
            base_url + '/asdflaerjd.html',
        ]
        for url in ok_urls:
            self.assertIsNotNone(extractor.extractFromURL(url))
        for url in fail_urls:
            with self.assertRaises(URLError):
                extractor.extractFromURL(url)

    def testLyricsCom(self):
        print()
        extractor = LyricsComExtractor()
        base_url = 'http://www.lyrics.com'
        ok_urls = [
            base_url + '/no-one-lyrics-alicia-keys.html',
            base_url + '/tnt-lyrics-acdc.html',
            base_url + '/cant-stop-the-feeling-lyrics-justin-timberlake.html',
            base_url + '/because-the-night-lyrics-10000-maniacs.html',
        ]
        fail_urls = [
            'http://anothersite.com/no-one-lyrics-alicia-keys.html',
            base_url + '/asdflaerjd.html',
        ]
        for url in ok_urls:
            self.assertIsNotNone(extractor.extractFromURL(url))
        for url in fail_urls:
            with self.assertRaises(URLError):
                extractor.extractFromURL(url)

    def testLyricsMode(self):
        print()
        extractor = LyricsModeExtractor()
        base_url = 'http://www.lyricsmode.com/lyrics'
        ok_urls = [
            base_url + '/a/alicia_keys/no_one.html',
            base_url + '/a/ac_dc/t_n_t.html',
            base_url + '/j/justin_timberlake/cant_stop_the_feeling.html',
            base_url + '/0-9/10000_maniacs/because_the_night.html',
        ]
        fail_urls = [
            'http://anothersite.com/a/alicia_keys/no_one.html',
            base_url + '/asdflaerjd.html',
        ]
        for url in ok_urls:
            self.assertIsNotNone(extractor.extractFromURL(url))
        for url in fail_urls:
            with self.assertRaises(URLError):
                extractor.extractFromURL(url)

    def testAZLyrics(self):
        print()
        extractor = AZLyricsExtractor()
        base_url = 'http://www.azlyrics.com/lyrics'
        ok_urls = [
            base_url + '/aliciakeys/noone.html',
            base_url + '/acdc/tnt.html',
            base_url + '/justintimberlake/cantstopthefeeling.html',
            base_url + '/10000maniacs/eatfortwo.html',
        ]
        fail_urls = [
            'http://anothersite.com/aliciakeys/noone.html',
            base_url + '/asdflaerjd.html',
        ]
        for url in ok_urls:
            self.assertIsNotNone(extractor.extractFromURL(url))
        for url in fail_urls:
            with self.assertRaises(URLError):
                extractor.extractFromURL(url)
