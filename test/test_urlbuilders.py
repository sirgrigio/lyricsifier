import unittest
from lyricsifier.utils import logging
from lyricsifier.core.urlbuilder \
    import MetroLyricsURLBuilder, LyricsComURLBuilder, \
    LyricsModeURLBuilder, AZLyricsURLBuilder


class TestURLBuilders(unittest.TestCase):

    def setUp(self):
        logging.loadCfg(default_path='logging_test.json')

    def testMetroLyrics(self):
        print()
        builder = MetroLyricsURLBuilder()
        base_url = 'http://www.metrolyrics.com'
        tracks = [
            {'artist': 'Alicia Keys',
             'title': 'No One',
             'url': base_url + '/no-one-lyrics-alicia-keys.html'},
            {'artist': 'AC/DC',
             'title': 'T.N.T.',
             'url': base_url + '/tnt-lyrics-acdc.html'},
            {'artist': 'Justin Timberlake',
             'title': 'Can\'t stop the feeling!',
             'url': base_url + '/cant-stop-the-feeling-lyrics-justin-timberlake.html'},
            {'artist': '10,000 maniacs',
             'title': 'Because The Night',
             'url': base_url + '/because-the-night-lyrics-10000-maniacs.html'},
        ]
        for t in tracks:
            self.assertEqual(t['url'], builder.build(t['artist'], t['title']))

    def testLyricsCom(self):
        print()
        builder = LyricsComURLBuilder()
        base_url = 'http://www.lyrics.com'
        tracks = [
            {'artist': 'Alicia Keys',
             'title': 'No One',
             'url': base_url + '/no-one-lyrics-alicia-keys.html'},
            {'artist': 'AC/DC',
             'title': 'T.N.T.',
             'url': base_url + '/tnt-lyrics-acdc.html'},
            {'artist': 'Justin Timberlake',
             'title': 'Can\'t stop the feeling!',
             'url': base_url + '/cant-stop-the-feeling-lyrics-justin-timberlake.html'},
            {'artist': '10,000 maniacs',
             'title': 'Because The Night',
             'url': base_url + '/because-the-night-lyrics-10000-maniacs.html'},
        ]
        for t in tracks:
            self.assertEqual(t['url'], builder.build(t['artist'], t['title']))

    def testLyricsMode(self):
        print()
        builder = LyricsModeURLBuilder()
        base_url = 'http://www.lyricsmode.com/lyrics'
        tracks = [
            {'artist': 'Alicia Keys',
             'title': 'No One',
             'url': base_url + '/a/alicia_keys/no_one.html'},
            {'artist': 'AC/DC',
             'title': 'T.N.T.',
             'url': base_url + '/a/ac_dc/t_n_t.html'},
            {'artist': 'Justin Timberlake',
             'title': 'Can\'t stop the feeling!',
             'url': base_url + '/j/justin_timberlake/cant_stop_the_feeling.html'},
            {'artist': '10,000 maniacs',
             'title': 'Because The Night',
             'url': base_url + '/0-9/10000_maniacs/because_the_night.html'},
        ]
        for t in tracks:
            self.assertEqual(t['url'], builder.build(t['artist'], t['title']))

    def testAZLyrics(self):
        print()
        builder = AZLyricsURLBuilder()
        base_url = 'http://www.azlyrics.com/lyrics'
        tracks = [
            {'artist': 'Alicia Keys',
             'title': 'No One',
             'url': base_url + '/aliciakeys/noone.html'},
            {'artist': 'AC/DC',
             'title': 'T.N.T.',
             'url': base_url + '/acdc/tnt.html'},
            {'artist': 'Justin Timberlake',
             'title': 'Can\'t stop the feeling!',
             'url': base_url + '/justintimberlake/cantstopthefeeling.html'},
            {'artist': '10,000 maniacs',
             'title': 'Eat For Two',
             'url': base_url + '/10000maniacs/eatfortwo.html'},
        ]
        for t in tracks:
            self.assertEqual(t['url'], builder.build(t['artist'], t['title']))
