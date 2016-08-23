import logging
import lyricsifier
from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
from cement.utils.misc import init_defaults
from lyricsifier.core.crawler import CrawlJob


class BaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'Attempt to classify songs by their lyrics'

    @expose(hide=True)
    def default(self):
        pass


class CrawlController(CementBaseController):
    class Meta:
        label = 'crawl'
        stacked_on = 'base'
        arguments = [
            (['-o', '--outdir'],
             dict(help='the output directory', action='store')),
            (['tracks'],
             dict(help='the tsv containing tracks id, artist and title', action='store', nargs=1)),
        ]

    @expose(help="crawl lyrics of given tracks")
    def crawl(self):
        if self.app.pargs.outdir:
            job = CrawlJob(self.app.pargs.tracks[0], self.app.pargs.outdir)
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
