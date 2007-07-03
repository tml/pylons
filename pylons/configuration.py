"""Configuration setup for templating systems and Paste error
middleware

This module supplies pylons_config which handles setting up defaults
for templating systems, Paste errorware, and prefixing Routes if
necessary.
"""
import os
import re
import warnings
import logging
log = logging.getLogger('pylons.config')

from paste.deploy.converters import asbool
from paste.config import DispatchingConfig

import pylons.legacy
import pylons.templating

default_template_engine = 'mako'
request_defaults = dict(charset=None, errors='strict',
                        decode_param_names=False,
                        language='en-us')
response_defaults = dict(content_type='text/html',
                         charset='utf-8', errors='strict')

class PylonsConfig(DispatchingConfig):
    """Pylons configuration object

    The Pylons configuration object is a per-application instance object
    that retains the information regarding the global and app conf's as
    well as per-application instance specific data such as the mapper, the
    paths for this instance, and the myghty configuration.

    The config object is available in your application as a Pylons global
    ``pylons_config`` under the ``g`` object. You can also import it from
    pylons with:

    .. code :: Python
        import pylons

        map = pylons.config['map']

    There's several useful keys of the config object most people will be
    interested in:

    ``template_options``
        Full dict of template options that any TG compatible plugin should
        be able to parse. Comes with basic config needed for Myghty, Kid,
        and Mako.
    ``map``
        Mapper object used for Routing. Yes, it is possible to add routes
        after your application has started running.
    ``paths``
        A dict of absolute paths that were defined in the applications
        ``config/environment.py`` module.
    ``environ_config``
        Dict of environ keys for where in the environ to pickup various
        objects for registering with Pylons. If these are present then
        PylonsApp will use them from environ rather than using default
        middleware from Beaker. Valid keys are: ``session, cache``
    ``template_engines``
        List of template engines to configure. The first one in the list will
        be configured as the default template engine. Each item in the list is
        a dict indicating how to configure the template engine with keys:
        ``engine``, ``template_root``, ``template_options``, and ``alias``
    ``default_charset``
        Deprecated: Use the response_settings dict instead.
        Default character encoding specified to the browser via the
        'charset' parameter of the HTTP response's Content-Type header.
    ``strict_c``
        Whether or not the ``c`` object should throw an attribute error when
        access is attempted to an attribute that doesn't exist.
    ``request_options``
        A dict of Content-Type related default settings for new instances of
        ``paste.wsgiwrappers.WSGIRequest``. May contain the values ``charset``
        and ``errors`` and ``decode_param_names``. Overrides the Pylons default
        values specified by the ``request_defaults`` dict.
    ``response_options``
        A dict of Content-Type related default settings for new instances of
        ``pylons.Response``. May contain the values ``content_type``,
        ``charset`` and ``errors``. Overrides the Pylons default values
        specified by the ``response_defaults`` dict.
    """
    defaults = {
        # The current project's package name
        'pylons.package': None,
        # The Routes?? only?? mapper
        'pylons.map': None,
        'pylons.paths': {},
        'pylons.g': None,
        'pylons.helpers': None, # should call this h or g
        'pylons.request_options': request_defaults.copy(), # just define these here
        'pylons.response_options': response_defaults.copy(),
        'pylons.environ_config': {}, # hrmph!
        'pylons.strict_c': False,
        'pylons.config_namespaces': {},
        'pylons.db_engines': {},
        'buffet.options': {},
        'buffet.template_engines': [],
        'buffet.template_options': {},
    }

    def __getattr__(self, name):
        # Backwards compatibility
        if name == 'Config':
            class FakeConfig(object):
                def __init__(this, *args, **kwargs):
                    self.load_environment(*args, **kwargs)
                def __getattr__(this, name):
                    return getattr(self, name)
                def __setattr__(this, name, value):
                    setattr(self, name, value)
            return FakeConfig
        else:
            conf_dict = self._current_obj()

            # Backwards compat for when the option is now in the dict, and
            # access was attempted via attribute
            for prefix in ('', 'pylons.', 'buffet.'):
                full_name = prefix + name
                if full_name in conf_dict:
                    warnings.warn(pylons.legacy.config_name_moved % \
                                      (name, full_name), DeprecationWarning, 2)
                    return conf_dict[full_name]
            return getattr(conf_dict, name)

    def load_environment(self, tmpl_options=None, map=None, paths=None,
                         environ_config=None, default_charset=None,
                         strict_c=False, request_settings=None,
                         response_settings=None):
        """Load the environment options"""
        conf = PylonsConfig.defaults.copy()
        if tmpl_options:
            conf['buffet.template_options'] = tmpl_options

        if request_settings:
            conf['pylons.request_options'].update(request_settings)

        if response_settings:
            conf['pylons.response_options'].update(response_settings)

        conf['pylons.map'] = map
        conf['pylons.paths'] = paths or {}
        conf['pylons.environ_config'] = environ_config or {}
        conf['pylons.strict_c'] = strict_c

        if default_charset:
            warnings.warn(pylons.legacy.default_charset_warning % \
                              dict(klass='Config', charset=default_charset),
                          DeprecationWarning, 2)
            conf['pylons.response_options']['charset'] = default_charset
        self['environment_load'] = conf

    def add_template_engine(self, engine, root, options=None, alias=None):
        """Add additional template engines for configuration on Pylons WSGI
        init.

        ``engine``
            The name of the template engine

        ``root``
            Template root for the engine

        ``options``
            Dict of additional options used during engine initialization, if
            not provided, default to using the template_options dict.

        ``alias``
            Name engine should respond to when actually used. This allows for
            multiple configurations of the same engine and lets you alias the
            additional ones to other names.

        Example of Kid addition:

        .. code-block:: Python

            # In yourproj/middleware.py
            # ...
            config.init_app(global_conf, app_conf, package='yourproj')

            # Load additional template engines
            kidopts = {'kid.assume_encoding':'utf-8', 'kid.encoding':'utf-8'}
            config.add_template_engine('kid', 'yourproj.kidtemplates', kidopts)

        Example of changing the default template engine:

        .. code-block:: Python

            # In yourproj/middleware.py
            # ...
            config.init_app(global_conf, app_conf, package='yourproj')

            # Remove existing template engine
            old_default = config.template_engines.pop()

            # Load additional template engines
            kidopts = {'kid.assume_encoding':'utf-8', 'kid.encoding':'utf-8'}
            config.add_template_engine('kid', 'yourproj.kidtemplates', kidopts)

            # Add old default as additional engine
            config.template_engines.append(old_default)
        """
        if not options:
            options = self['buffet.template_options']
        config = dict(engine=engine, template_root=root,
            template_options=options, alias=alias)
        self['buffet.template_engines'].append(config)

    def init_app(self, global_conf, app_conf, package=None,
                 template_engine=default_template_engine, paths=None):
        """Initialize configuration for the application

        ``global_config``
            Several options are expected to be set for a Pylons web
            application. They will be loaded from the global_config which has
            the main Paste options. If ``debug`` is not enabled as a global
            config option, the following option *must* be set:

            * error_to - The email address to send the debug error to

            The optional config options in this case are:

            * smtp_server - The SMTP server to use, defaults to 'localhost'
            * error_log - A logfile to write the error to
            * error_subject_prefix - The prefix of the error email subject
            * from_address - Whom the error email should be from
        ``app_conf``
            Defaults supplied via the [app:main] section from the Paste
            config file. ``load_config`` only cares about whether a 'prefix'
            option is set, if so it will update Routes to ensure URL's take
            that into account.
        ``package``
            The name of the application package, to be stored in the app_conf.
        ``template_engine``
            Declare the default template engine to setup. Choices are kid,
            genshi, mako (the default), and pylonsmyghty.
        """
        conf = global_conf.copy()
        conf.update(app_conf)
        conf.update(dict(app_conf=app_conf, global_conf=global_conf))
        conf.update(self.pop('environment_load', {}))
        
        if paths:
            conf['pylons.paths'] = paths
        
        # XXX Legacy: More backwards compatibility locations for the package
        #             name
        conf['pylons.package'] = conf['package'] = conf['app_conf']['package'] = package
        
        self.push_process_config(conf)
        self.set_defaults(template_engine)
    
    def set_defaults(self, template_engine):
        conf = self._current_obj()
        # Ensure all the keys from defaults are present, load them if not
        for key, val in PylonsConfig.defaults.iteritems():
            conf.setdefault(key, val)

        # Setup the prefix to override the routes if necessary.
        prefix = self.get('prefix')
        if prefix:
            warnings.warn(pylons.legacy.prefix_warning % prefix,
                          DeprecationWarning, 2)
            conf['pylons.map'].prefix = app_conf['prefix']
            conf['pylons.map']._created_regs = False

        errorware = {}
        # Load the errorware configuration from the Paste configuration file
        # These all have defaults, and emails are only sent if configured and
        # if this application is running in production mode
        errorware['debug'] = asbool(conf.get('debug'))
        if not errorware['debug']:
            errorware['debug'] = False
            errorware['error_email'] = conf.get('email_to')
            errorware['error_log'] = conf.get('error_log', None)
            errorware['smtp_server'] = conf.get('smtp_server',
                'localhost')
            errorware['error_subject_prefix'] = conf.get(
                'error_subject_prefix', 'WebApp Error: ')
            errorware['from_address'] = conf.get('from_address',
                global_conf.get('error_email_from', 'pylons@yourapp.com'))
            errorware['error_message'] = conf.get('error_message',
                'An internal server error occurred')

        # Standard Pylons configuration directives for Myghty
        myghty_defaults = {}

        # Raise a complete error for the error middleware to catch
        myghty_defaults['raise_error'] = True
        myghty_defaults['output_encoding'] = conf['pylons.response_options']['charset']
        myghty_defaults['component_root'] = [{os.path.basename(path): path} \
            for path in conf['pylons.paths']['templates']]

        # Merge additional globals
        myghty_defaults.setdefault('allow_globals',
                                   []).extend(pylons.templating.PYLONS_VARS)

        myghty_template_options = {}
        if 'myghty_data_dir' in conf:
            warnings.warn("Old config option found in ini file, replace "
                          "'myghty_data_dir' option with 'data_dir'",
                          DeprecationWarning, 2)
            myghty_defaults['data_dir'] = conf['myghty_data_dir']
        elif 'cache_dir' in conf:
            myghty_defaults['data_dir'] = os.path.join(conf['cache_dir'],
                'templates')

        # Copy in some defaults
        if 'cache_dir' in conf:
            conf.setdefault('beaker.session.data_dir',
                            os.path.join(conf['cache_dir'], 'sessions'))
            conf.setdefault('beaker.cache.data_dir',
                            os.path.join(conf['cache_dir'], 'cache'))

        # Copy Myghty defaults and options into template options
        for k, v in myghty_defaults.iteritems():
            myghty_template_options['myghty.'+k] = v

            # Legacy copy of session and cache settings into conf
            if k.startswith('session_') or k.startswith('cache_'):
                conf[k] = v

        # Copy old session/cache config to new keys for Beaker 0.7+
        for key, val in conf.items():
            if key.startswith('cache_'):
                conf['cache.'+key[6:]] = val
            elif key.startswith('session_'):
                conf['session.'+key[8:]] = val

        # Setup the main template options dict
        conf['buffet.template_options'].update(myghty_template_options)

        # Setup several defaults for various template languages
        defaults = {}

        # Rearrange template options as default for Mako
        defaults['mako.directories'] = conf['pylons.paths']['templates']
        defaults['mako.filesystem_checks'] = True
        defaults['mako.output_encoding'] = \
            conf['pylons.response_options']['charset']
        if 'cache_dir' in conf:
            defaults['mako.module_directory'] = \
                os.path.join(conf['cache_dir'], 'templates')

        # Setup kid defaults
        defaults['kid.assume_encoding'] = 'utf-8'
        defaults['kid.encoding'] = conf['pylons.response_options']['charset']

        # Merge template options into defaults
        defaults.update(conf['buffet.template_options'])
        conf['buffet.template_options'] = defaults

        # Prepare our default template engine
        if template_engine == 'pylonsmyghty':
            self.add_template_engine('pylonsmyghty', None,
                                     myghty_template_options)
        elif template_engine == 'mako':
            self.add_template_engine('mako', '')
        elif template_engine in ['genshi', 'kid']:
            self.add_template_engine(template_engine, conf['pylons.package'] + '.templates')

        # Save our errorware values
        conf['pylons.errorware'] = errorware

config = PylonsConfig()

# Push an empty config so all accesses to config at import time
# have something to look at and modify. This config will be merged with the
# app's when it's built in the paste.app_factory entry point.
initial_config = {'default_template_engine':default_template_engine,
                  'pylons.db_engines':{}}
config.push_process_config(initial_config)