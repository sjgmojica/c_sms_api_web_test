"""
The configuration loads 'settings.yaml' from the current working directory

Configuratioin class depends on tornado's config type (debug, staging,
production), on every python script that has '__main__' the Configuration 
must be initialized
AFTER parsing tornado's options:

    tornado.options.parse_command_line()
    Configuration.initialize()
    http_server = tornado.httpserver.HTTPServer(
                                        Application(Configuration.values()))

During runtime the Configuration settings can be updated by calling
Configuration.initialize once again and the new settings will be applied.
The URL link!!! MUST!!! be secured and can only be called within the internal
network!

Application usage example:

    # Get domain name
    domain_name = Configuration.config('domain')

    # Get facebook as dict
    facebook_config = Configuration.config('facebook')
    fb_app_id = facebook_config['app_id']
    fb_api_key = facebook_config['api_key']
    fb_secret = facebook_config['secret']

    # Get okspinoy callback_url (fast access to a single sub-item)
    okspinoy_callback_url = Configuration.get_config('okspinoy',
                                                     'callback_url')

    # Get an 'application-level' config (i.e. session_expiration)
    session_expiration = Configuration.app_config('session_expiration')
"""
import yaml
import urllib2
#import os

from tornado.options import options, parse_command_line
from pprint import pprint

# Define yaml location via http.
YAML_LOCATIONS = {
    'staging': {'host': '127.0.0.1', 'port': ''},
    'debug':  {'host': '127.0.0.1', 'port': ''},
    'prod':  {'host': '127.0.0.1', 'port': ''}
}

# Define list of configuration types. List item corresponds to the 
# directory name inside the config directory.
CONFIG_TYPES = ["prod", "debug", "staging"]

# Config paths. Define directory name of the configuration to be used
LOCAL_CONFIG = "config/%s/settings.yaml"
HTTP_CONFIG = "http://%s/%s/settings.yaml"
CONFIG = 'prod'

def yaml_loader(location):
    data = None
    try:
        response = urllib2.urlopen(location)
        config = response.read()
        data = yaml.safe_load_all(config).next()
    except:
        data = yaml.safe_load_all(open(location)).next()
    return data

class Configuration(object):
    """Loads and holds the application settings."""
    
    _values = None
    _config = None
    _app_config = None 
    
    @staticmethod
    def initialize():
        """Load corresponding settings.yaml""" 
        # If passed options.config is in CONFIG_TYPES, do check local_settings
        
        parse_command_line()
        
        if options.config in CONFIG_TYPES:
        # if CONFIG in CONFIG_TYPES:
            # if local_settings value is true
            # load the yaml locally otherwise load it from the
            # specified yaml host via http. Yaml http location
            # is defined by HTTP_CONFIG
            if options.local_settings == 'true':
                Configuration._values = Configuration.load_locally()
            else:
                try:
                    # Retrieve yaml host definition
                    yaml_loc = YAML_LOCATIONS[options.config]
                    url = None
                    
                    # Build the url
                    if yaml_loc.get('host', None) and yaml_loc.get('port'):
                        url = HTTP_CONFIG % ("%s:%s" % (yaml_loc['host'], yaml_loc['port']), str(options.config))
                    elif yaml_loc.get('host', None) and not yaml_loc.get('port'):
                        url = HTTP_CONFIG % (yaml_loc['host'], str(options.config))
                    
                    # Retrieve the yaml via GET method.
                    # if retrieval fails or an exception occurs switch to local yaml
                    if url:
                        response = urllib2.urlopen(url) 
                        config = response.read()
                        Configuration._values = yaml.safe_load_all(config).next()
                    else:
                        Configuration._values = Configuration.load_locally()
                except:
                    Configuration._values = Configuration.load_locally()
        else:
            if options.local_settings == 'true':
                try:
                    Configuration._values = yaml.safe_load_all(open('settings.yaml')).next()
                except Exception, e:
                    print e 
            else:
                try:
                    yaml_loc = YAML_LOCATIONS[options.config]
                    # Build the url
                    if yaml_loc.get('host', None) and yaml_loc.get('port'):
                        url = HTTP_CONFIG % ("%s:%s" % (yaml_loc['host'], yaml_loc['port']), str(options.config))
                    elif yaml_loc.get('host', None) and not yaml_loc.get('port'):
                        url = HTTP_CONFIG % (yaml_loc['host'], str(options.config))
                    response = urllib2.urlopen(url) 
                    config = response.read()
                    Configuration._values = yaml.safe_load_all(config).next()
                except:
                    Configuration._values = yaml.safe_load_all(open('settings.yaml')).next()
        
        # Configuration._config = Configuration._values[options.config]
        Configuration._config = Configuration._values

    @staticmethod
    def load_locally():
        conf_file = LOCAL_CONFIG % str(options.config)
        return yaml.safe_load_all(open(conf_file)).next()
    
    @staticmethod
    def values():
        """Returns the values of Configuration"""
        return Configuration._values

    @staticmethod
    def config():
        """Returns the values of main"""
        return Configuration._config

    @staticmethod
    def get_config(main, sub):
        """Returns the values of main sub"""
        return Configuration._config[main][sub]
