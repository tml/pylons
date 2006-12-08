"""``etag_cache``, ``redirect_to``, and ``abort`` methods

Additional helper object available for use in Controllers is the etag_cache.
"""
import os.path
import paste.httpexceptions as httpexceptions
from gettext import NullTranslations
from pkg_resources import resource_exists
from paste.deploy.config import CONFIG
from routes import redirect_to

import pylons
from pylons.i18n.translation import egg_translation

class LanguageError(Exception):
    """Exception raised when a problem occurs with changing languages"""
    pass

def gettext(value):
    """Mark a string for translation. Returns the localized string of value.
    
    Mark a string to be localized as follows:
    
    .. code-block:: Python
    
        gettext('This should be in lots of languages')
    """
    return pylons.translator.gettext(value)

def ugettext(value):
    """Mark a string for translation. Returns the localized unicode string of
    value.
    
    Mark a string to be localized as follows:
    
    .. code-block:: Python
    
        _('This should be in lots of languages')
    """
    return pylons.translator.ugettext(value)
_ = ugettext

def ngettext(singular, plural, n):
    """Mark a string for translation. Returns the localized string of the
    pluralized value.

    This does a plural-forms lookup of a message id. ``singular`` is used as
    the message id for purposes of lookup in the catalog, while ``n`` is used
    to determine which plural form to use. The returned message is a string.
    
    Mark a string to be localized as follows:
    
    .. code-block:: Python
    
        ngettext('There is %(num)d file here', 'There are %(num)d files here',
                 n) % {'num': n}
    """
    return pylons.translator.ngettext(singular, plural, n)

def ungettext(singular, plural, n):
    """Mark a string for translation. Returns the localized unicode string of
    the pluralized value.

    This does a plural-forms lookup of a message id. ``singular`` is used as
    the message id for purposes of lookup in the catalog, while ``n`` is used
    to determine which plural form to use. The returned message is a Unicode
    string.
    
    Mark a string to be localized as follows:
    
    .. code-block:: Python
    
        ungettext('There is %(num)d file here', 'There are %(num)d files here',
                  n) % {'num': n}
    """
    return pylons.translator.ungettext(singular, plural, n)

def log(msg):
    """Log a message to the output log."""
    pylons.request.environ['wsgi.errors'].write('=> %s\n' % str(msg))

def set_lang(lang):
    """Set the i18n language used"""
    registry = pylons.request.environ['paste.registry']
    if lang is None:
        registry.replace(pylons.translator, NullTranslations())
    else:
        project_name = CONFIG['app_conf']['package']
        catalog_path = os.path.join('i18n', lang, 'LC_MESSAGES')
        if not resource_exists(project_name, catalog_path):
            raise LanguageError('Language catalog %s not found' % \
                                os.path.join(project_name, catalog_path))
        translator = egg_translation(project_name, lang=catalog_path)
        translator.pylons_lang = lang
        registry.replace(pylons.translator, translator)

def get_lang():
    """Return the current i18n language used"""
    return getattr(pylons.translator, 'pylons_lang', None)

def etag_cache(key=None):
    """Use the HTTP Entity Tag cache for Browser side caching
    
    If a "If-None-Match" header is found, and equivilant to ``key``, then
    a ``304`` HTTP message will be returned with the ETag to tell the browser
    that it should use its current cache of the page.
    
    Otherwise, the ETag header will be added to a new response object and
    returned for use in your action.
    
    Suggested use is within a Controller Action like so:
    
    .. code-block:: Python
    
        import pylons
        
        class YourController(BaseController):
            def index(self):
                resp = etag_cache(key=1)
                resp.write(render('/splash.myt'))
                return resp
    
    .. Note:: 
        This works because etag_cache will raise an HTTPNotModified
        exception if the ETag recieved matches the key provided.
    """
    if_none_match = pylons.request.environ.get('HTTP_IF_NONE_MATCH', None)
    resp = pylons.Response()
    resp.headers['ETag'] = key
    if str(key) == if_none_match:
        raise httpexceptions.HTTPNotModified()
    else:
        return resp

def abort(status_code=None, detail="", headers=None, comment=None):
    """Aborts the request immediately by returning an HTTP exception
    
    In the event that the status_code is a 300 series error, the detail 
    attribute will be used as the Location header should one not be specified
    in the headers attribute.
    """
    exc = httpexceptions.get_exception(status_code)(detail, headers, comment)
    raise exc

__all__ = ['etag_cache', 'redirect_to', 'abort', '_', 'ungettext', 'log',
           'set_lang', 'get_lang']
