from cement.core.foundation import CementApp
from cement.ext.ext_argparse import ArgparseController, expose
from lyricsifier.core.crawler import MetroLyricsCrawler
from lyricsifier.core.job import ExtractJob, TagJob
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
                help='the max amount of seconds between two requests (default 300)',
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
        job = TagJob(
            self.app.pargs.file[0],
            self.app.pargs.output_file,
            processes=int(self.app.pargs.processes)
        )
        job.start()


class LyricsifierApp(CementApp):
    class Meta:
        label = 'lyricsifier'
        arguments_override_config = True
        base_controller = 'base'
        handlers = [BaseController, CrawlController,
                    ExtractController, TagController]


def main():
    with LyricsifierApp() as app:
        logging.loadcfg()
        app.setup()
        app.run()

if __name__ == '__main__':
    main()
