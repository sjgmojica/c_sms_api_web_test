'''
    @author: Jhesed Tacadena
    @date: 2013-11
    @description:
        - contains collection of offline processes.
        - this file will run all of the processes
        defined in __main__
'''

from tornado.options import define, options, parse_command_line, print_help
from features.checkout_updater.checkout_updater import start_checkout_updater
from features.suffix_updater.free_suffix_updater import start_suffix_free_updater
from features.suffix_updater.paid_to_inactive_suffix_updater import start_suffix_paid_to_inactive_updater
from features.suffix_updater.unpaid_to_inactive_suffix_updater import start_suffix_unpaid_to_inactive_updater
from features.email_notifier.email_notifier import start_email_notifiers

# define("config", default='debug', help="run configuration settings", type=str) 
# define("log_method", default='file', help="file | scribe | both", type=str)
# define("local_settings", default="true", help="enable/disable use of local settings", type=str)
# define("port", default=80, help="run on the given port", type=int)

if __name__ == '__main__':
    
    print '\n ---- start: email notifiers --- \n'
    start_email_notifiers()