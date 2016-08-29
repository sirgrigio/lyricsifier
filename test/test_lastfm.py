import unittest
from lyricsifier.utils import logging, lastfm


class TestLastFM(unittest.TestCase):

    def setUp(self):
        logging.loadcfg(default_path='logging_test.json')
        self.api_key = 'ac5188f22006a4ef88c6b83746b11118'

    def test_ok(self):
        print()
        tracks = [
            {'artist': 'Alicia Keys',
             'title': 'No One',
             'tag': 'soul'},
            {'artist': 'AC/DC',
             'title': 'T.N.T.',
             'tag': 'hard rock'},
            {'artist': 'Justin Timberlake',
             'title': 'Can\'t stop the feeling!',
             'tag': 'pop'},
            {'artist': '10,000 maniacs',
             'title': 'Because The Night',
             'tag': 'covers'},
        ]
        for track in tracks:
            self.assertEqual(
                track['tag'],
                lastfm.get_tag(self.api_key, track['artist'], track['title'])
            )

    def test_fail(self):
        print()
        artist = 'NoArtistWithThisName'
        track = 'NoSongWithThisTitle'
        self.assertIsNone(lastfm.get_tag(self.api_key, artist, track))
