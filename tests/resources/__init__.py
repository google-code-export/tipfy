from tipfy.ext.genshi import Genshi
from jinja2 import FileSystemLoader, Environment
from mako.lookup import TemplateLookup

from tipfy import Tipfy

def get_genshi_env():
    return Genshi()


def get_jinja2_env():
    app = Tipfy.app
    cfg = app.get_config('tipfy.ext.jinja2')

    loader = FileSystemLoader(cfg.get( 'templates_dir'))

    return Environment(loader=loader)


def get_mako_env():
    app = Tipfy.app
    dirs = app.get_config('tipfy.ext.mako', 'templates_dir')
    if isinstance(dirs, basestring):
        dirs = [dirs]

    return TemplateLookup(directories=dirs, output_encoding='utf-8',
        encoding_errors='replace')



