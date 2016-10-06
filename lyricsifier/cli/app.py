from cement.core.foundation import CementApp
from cement.ext.ext_argparse import ArgparseController, expose
from lyricsifier.core.crawler import MetroLyricsCrawler
from lyricsifier.core.job \
    import ClassifyJob, ClusterJob, ExtractJob, TagJob, VectorizeJob
from lyricsifier.cli.utils import logging


class BaseController(ArgparseController):
    class Meta:
        label = 'base'
        description = 'Attempt to classify songs by their lyrics'

    @expose(hide=True)
    def default(self):
        pass


class CrawlController(ArgparseController):
    class Meta:
        label = 'crawl'
        stacked_on = 'base'

    @expose(hide=True)
    def default(self):
        pass

    @expose(
        help="crawl lyrics URL from metrolyrics.com",
        arguments=[
            (['-o', '--output-file'],
             dict(
                help='the output file (default ./target/metrolyrics.tsv)',
                action='store',
                default='./target/metrolyrics.tsv')
             ),
            (['-d', '--max-delay'],
             dict(
                help='''the max amount of seconds between two requests
                        (default 300)''',
                action='store',
                default=300)
             ),
        ]
    )
    def crawl(self):
        crawler = MetroLyricsCrawler(
            self.app.pargs.output_file,
            int(self.app.pargs.max_delay)
        )
        crawler.crawl()


class ExtractController(ArgparseController):
    class Meta:
        label = 'extract'
        stacked_on = 'base'

    @expose(hide=True)
    def default(self):
        pass

    @expose(
        help="extract lyrics from urls",
        arguments=[
            (['-o', '--output-file'],
             dict(
                help='the output file (default ./target/lyrics.tsv)',
                action='store',
                default='./target/lyrics.tsv')
             ),
            (['-p', '--processes'],
             dict(
                help='number of parallel processes (default 1)',
                action='store',
                default=1)
             ),
            (['file'],
             dict(
                help='a tsv file containing the lyrics urls',
                action='store',
                nargs=1)
             ),
        ]
    )
    def extract(self):
        job = ExtractJob(
            self.app.pargs.file[0],
            self.app.pargs.output_file,
            processes=int(self.app.pargs.processes)
        )
        job.start()


class TagController(ArgparseController):
    class Meta:
        label = 'tag'
        stacked_on = 'base'

    @expose(hide=True)
    def default(self):
        pass

    @expose(
        help="tag the given tracks",
        arguments=[
            (['-g', '--genres-file'],
             dict(
                help='''a json file containing genres hierarchy
                        (default ./genres.json)''',
                action='store',
                default='./genres.json')
             ),
            (['-o', '--output-file'],
             dict(
                help='the output file (default ./target/tags.tsv)',
                action='store',
                default='./target/tags.tsv')
             ),
            (['-p', '--processes'],
             dict(
                help='number of parallel processes (default 1)',
                action='store',
                default=1)
             ),
            (['file'],
             dict(
                help='a tsv file containing tracks id, artist and title',
                action='store',
                nargs=1)
             ),
        ]
    )
    def tag(self):
        import json
        from lyricsifier.core.tagger import LastFMTagger
        genres = {}
        with open(self.app.pargs.genres_file, 'r', encoding='utf8') as f:
            genres_json = json.load(f)
            genres = {g['genre']: g['subgenres'] for g in genres_json}
        tagger = LastFMTagger(
            'ac5188f22006a4ef88c6b83746b11118',
            genres
        )
        job = TagJob(
            self.app.pargs.file[0],
            self.app.pargs.output_file,
            taggers=[tagger, ],
            processes=int(self.app.pargs.processes)
        )
        job.start()


class ClusterController(ArgparseController):
    class Meta:
        label = 'cluster'
        stacked_on = 'base'

    @expose(hide=True)
    def default(self):
        pass

    @expose(
        help="cluster the dataset",
        arguments=[
            (['dataset_file'],
             dict(
                help='the file containg the dataset',
                action='store')
             ),
            (['-p', '--processes'],
             dict(
                help='number of parallel processes (default 1)',
                action='store',
                default=1)
             ),
        ]
    )
    def cluster(self):
        job = ClusterJob(
            self.app.pargs.dataset_file,
            processes=int(self.app.pargs.processes),
        )
        job.start()


class ClassifyController(ArgparseController):
    class Meta:
        label = 'classify'
        stacked_on = 'base'

    @expose(hide=True)
    def default(self):
        pass

    @expose(
        help="classify the testset upon training on the trainset",
        arguments=[
            (['trainset_file'],
             dict(
                help='the file containg the trainset',
                action='store')
             ),
            (['testset_file'],
             dict(
                help='the file containg the testset',
                action='store')
             ),
            (['-r', '--report-dir'],
             dict(
                help='''the directory to save the reports to
                        (default ./target/report/)''',
                action='store',
                default='./target/report/')
             ),
            (['-p', '--processes'],
             dict(
                help='number of parallel processes (default 1)',
                action='store',
                default=1)
             ),
        ]
    )
    def classify(self):
        job = ClassifyJob(
            self.app.pargs.trainset_file,
            self.app.pargs.testset_file,
            self.app.pargs.report_dir,
            processes=int(self.app.pargs.processes)
        )
        job.start()


class VectorizeController(ArgparseController):
    class Meta:
        label = 'vectorize'
        stacked_on = 'base'

    @expose(hide=True)
    def default(self):
        pass

    @expose(
        help="create a vectorize dataset",
        arguments=[
            (['lyrics_file'],
             dict(
                help='the file containg lyrics',
                action='store')
             ),
            (['tasg_file'],
             dict(
                help='the file containg tags',
                action='store')
             ),
            (['-o', '--outdir'],
             dict(
                help='''the directory to save the datasets to
                        (default ./target/datasets/)''',
                action='store',
                default='./target/datasets/')
             ),
            (['-s', '--split'],
             dict(
                help='''wheter to create or not both trainset and testset
                        (default False)''',
                action='store_true',
                default=False)
             ),
        ]
    )
    def vectorize(self):
        job = VectorizeJob(
            self.app.pargs.lyrics_file,
            self.app.pargs.tasg_file,
            self.app.pargs.outdir,
            split=self.app.pargs.split
        )
        job.start()


class LyricsifierApp(CementApp):
    class Meta:
        label = 'lyricsifier'
        arguments_override_config = True
        base_controller = 'base'
        handlers = [BaseController, ClassifyController, ClusterController,
                    CrawlController, ExtractController, TagController,
                    VectorizeController]


def main():
    with LyricsifierApp() as app:
        logging.loadcfg()
        app.setup()
        app.run()


if __name__ == '__main__':
    main()
