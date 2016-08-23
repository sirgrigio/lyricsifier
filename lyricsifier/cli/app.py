import logging
import lyricsifier
from cement.core.foundation import CementApp
from cement.ext.ext_argparse import ArgparseController, expose
from cement.utils.misc import init_defaults
from lyricsifier.core.crawler import CrawlJob


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
        help="crawl lyrics of given tracks",
        arguments=[
            (['-o', '--outdir'],
             dict(help='the output directory', action='store')),
            (['-a', '--attempts'],
             dict(help='the number of attempts allowed for each crawler (default 3)', action='store', default=3)),
            (['tracks'],
             dict(help='the tsv containing tracks id, artist and title', action='store', nargs=1)),
        ]
    )
    def crawl(self):
        if self.app.pargs.outdir:
            attempts = int(self.app.pargs.attempts)
            job = CrawlJob(self.app.pargs.tracks[0], 
                           self.app.pargs.outdir,
                           attempts=attempts)
            job.run()
        else:
            self.app.log.warning('missing output directory')


class LyricsifierApp(CementApp):
    class Meta:
        label = 'lyricsifier'
        arguments_override_config = True
        base_controller = 'base'
        handlers = [BaseController, CrawlController]


def configure_log(level=logging.DEBUG):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s (%(levelname)s) %(name)s : %(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger('lyricsifier')
    log.setLevel(level)
    log.addHandler(handler)


def main():
    with LyricsifierApp() as app:
        logLevel = logging.DEBUG if app.debug else logging.WARNING
        configure_log(logLevel)
        app.setup()
        app.run()

if __name__ == '__main__':
    main()
