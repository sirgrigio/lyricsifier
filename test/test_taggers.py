import json
import unittest
from lyricsifier.core.tagger import LastFMTagger
from lyricsifier.cli.utils import logging


class TestLastFM(unittest.TestCase):

    def setUp(self):
        logging.loadcfg(default_path='logging_test.json')
        lastfm_api_key = 'ac5188f22006a4ef88c6b83746b11118'
        with open('genres.json', 'r', encoding='utf8') as f:
            genres_json = json.load(f)
            genres = {g['genre']: g['subgenres'] for g in genres_json}
            self.taggers = [LastFMTagger(lastfm_api_key, genres), ]

    def test_ok(self):
        print()
        tracks = [
            {'artist': 'Alicia Keys',
             'title': 'No One',
             'tag': 'r&b'},
            {'artist': 'AC/DC',
             'title': 'T.N.T.',
             'tag': 'rock'},
            {'artist': 'Justin Timberlake',
             'title': 'Can\'t stop the feeling!',
             'tag': 'pop'},
            {'artist': '10,000 maniacs',
             'title': 'Because The Night',
             'tag': 'rock'},
        ]
        artists = [
            {'artist': 'Alicia Keys',
             'tag': 'r&b'},
            {'artist': 'Cher',
             'tag': 'pop'},
        ]
        for track in tracks:
            for tagger in self.taggers:
                self.assertEqual(
                    track['tag'],
                    tagger.tagTrack(track['artist'], track['title'])
                )
        for artist in artists:
            for tagger in self.taggers:
                self.assertEqual(
                    artist['tag'],
                    tagger.tagArtist(artist['artist'])
                )

    def test_fail(self):
        print()
        artist = 'NoArtistWithThisName'
        track = 'NoSongWithThisTitle'
        for tagger in self.taggers:
            self.assertIsNone(tagger.tagTrack(artist, track))
            self.assertIsNone(tagger.tagArtist(artist))
