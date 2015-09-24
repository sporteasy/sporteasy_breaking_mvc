from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils import autoreload
import rpyc
import cPickle as pickle
from sporteasy_breaking_mvc.utils.proxy import get_endpoint_class
from rpyc.utils.server import ThreadedServer


class CallService(rpyc.Service):
    """
    Rpyc service implementation
    """

    def on_connect(self):
        """
        Called when the connection is established
        """
        print "client connected."

    def on_disconnect(self):
        """
        Called when the connection had already terminated for cleanup
        (must not perform any IO on the connection)
        """
        print "client disconnected."

    def exposed_call(self, service, method, params):
        """
        Forwards calls to services endpoints and return the result.
        """
        args, kwargs = pickle.loads(params)
        print 'calling {}.{}'.format(service, method)
        endpoint = get_endpoint_class(service)()
        result = getattr(endpoint, method)(*args, **kwargs)
        return pickle.dumps(result)


class Command(BaseCommand):
    """
    Starts serviced
    """

    option_list = BaseCommand.option_list + (
        make_option('--noreload', action='store_false', dest='use_reloader', default=True,
                    help='Tells Django to NOT use the auto-reloader.'),
    )
    help = "Starts serviced."
    args = '[optional ipaddr:port]'

    def handle(self, *args, **options):
        """
        Handles serviced command with autoreload feature.
        """
        use_reloader = options.get('use_reloader')

        if use_reloader:
            autoreload.main(self.inner_run, args, options)
        else:
            self.inner_run(*args, **options)

    def inner_run(self, *args, **options):
        """
        Starts a threaded server on given hostname:port (defaults to 127.0.0.1:4444)
        """

        # defaults
        hostname = '0.0.0.0'
        port = '4444'

        if len(args) == 1:
            hostname, port = args[0].split(':')

        print "Starting serviced on {}:{}".format(hostname, port)
        server = ThreadedServer(CallService, port=int(port))
        server.start()
