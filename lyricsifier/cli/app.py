from cement.core.foundation import CementApp
from cement.ext.ext_argparse import ArgparseController, expose
from lyricsifier.core.crawler import MetroLyricsCrawler
from lyricsifier.utils import logging


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
                help='the output file (default ./target/metrolyrics.txt)',
                action='store',
                default='./target/metrolyrics.txt')
             ),
        ]
    )
    def crawl(self):
        crawler = MetroLyricsCrawler(self.app.pargs.output_file)
        crawler.crawl()


class LyricsifierApp(CementApp):
    class Meta:
        label = 'lyricsifier'
        arguments_override_config = True
        base_controller = 'base'
        handlers = [BaseController, CrawlController]


def main():
    with LyricsifierApp() as app:
        logging.loadCfg()
        app.setup()
        app.run()

if __name__ == '__main__':
    main()
