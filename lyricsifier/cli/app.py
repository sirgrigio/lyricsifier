import logging
from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
from cement.utils.misc import init_defaults

defaults = init_defaults('lyricsifier', 'crawler')
defaults['crawler']['tsv'] = None
defaults['crawler']['outdir'] = None


class BaseController(CementBaseController):
    class Meta:
        label = 'base'

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
            (['extra_arguments'],
             dict(action='store', nargs='*')),
        ]

    @expose(help="crawl lyrics of given tracks")
    def crawl(self):
        if self.app.pargs.extra_arguments and self.app.pargs.outdir:
            pass


class LyricsifierApp(CementApp):
    class Meta:
        label = 'lyricsifier'
        config_defaults = defaults
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
        app.run()
        logLevel = logging.DEBUG if app.debug else logging.WARNING
        configure_log(logLevel)

if __name__ == '__main__':
    main()
