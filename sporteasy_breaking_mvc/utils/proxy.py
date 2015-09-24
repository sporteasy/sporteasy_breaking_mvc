import sys
import re
import rpyc
import cPickle as pickle
from threading import local
from django.conf import settings
from django.core.urlresolvers import reverse
import django.dispatch


call_started = django.dispatch.Signal(providing_args=['service', 'method', 'args', 'kwargs'])
call_finished = django.dispatch.Signal(providing_args=['return'])


def _get_endpoint_class_name(service_name):
    def camelize(msg):
        """
        >>> 'service_name'
        ServiceName
        """
        words = re.split('_', msg)
        return ''.join([word.capitalize() for word in words])
    return '{}ServiceEndpoint'.format(camelize(service_name))


def get_endpoint_class(service_name):
    """
    Returns the class definition for a given service
    """
    module_name = '{}.core.services.{}'.format(__name__.split('.')[0], service_name)

    # import endpoint module if necessary
    if not module_name in sys.modules:
        __import__(module_name)

    return getattr(sys.modules[module_name], _get_endpoint_class_name(service_name))


class ServiceContainer(object):

    def __init__(self, config=None):
        self._services = local()  # thread local storage
        self._config = config

    def __getattr__(self, name):
        if name in self._config:
            # Create a service proxy instance if not cached yet
            if not hasattr(self._services, name):
                config = self._config[name]
                proxy_class_instance = getattr(sys.modules[__name__], config['PROXY']['CLASS'])
                proxy_instance = proxy_class_instance(name, **config['PROXY']['OPTIONS'])
                setattr(self._services, name, proxy_instance)

            return getattr(self._services, name)
        else:
            raise AttributeError(name)

    def get_services_list(self, **request):
        """Return list of all available services. If request is not null,
        return a dictionary"""

        services = self._config.keys()
        if request:
            method_call = '?method=' + request['root_name'] + '.'
            return {'services': services, 'url': reverse('service-view') + method_call}
        else:
            return services


# Create a ServiceContainer instance. It will be shared by all threads.
service = ServiceContainer(settings.SERVICES)


class ServiceProxy(object):
    """
    This is an abstract class defining ServiceProxy interface.
    """
    def __init__(self, name, **kwargs):
        self.name = name  # service name as stored in the config

    def __getattr__(self, name):
        """
        When you call service.foo(), service being a ServiceProxy class instance, python internally calls
        service.__getattr__ method because ServiceProxy has no foo() method defined. It makes possible
        for our proxy to return a function that will actually handle the call.
        """
        raise NotImplementedError


class LocalServiceInvocation(object):

    def __init__(self, endpoint_instance, service_name, method_name):
        self._endpoint_instance = endpoint_instance
        self._service_name = service_name
        self._method_name = method_name

    def __call__(self, *args, **kwargs):
        """
        Actually calls the real method
        """
        call_started.send(sender=self, service=self._service_name, method=self._method_name, args=args, kwargs=kwargs)
        result = getattr(self._endpoint_instance, self._method_name)(*args, **kwargs)
        call_finished.send(sender=self, result=result)
        return result


class LocalServiceProxy(ServiceProxy):

    def __init__(self, name, **kwargs):
        super(LocalServiceProxy, self).__init__(name, **kwargs)

        self._endpoint_instance = get_endpoint_class(name)()
        self._invocations = {}

    def __getattr__(self, method_name):
        if not method_name in self._invocations:
            self._invocations[method_name] = LocalServiceInvocation(self._endpoint_instance, self.name, method_name)

        return self._invocations[method_name].__call__


class RpycServiceInvocation(object):

    def __init__(self, client, service_name, method_name, root_url):
        self._client = client
        self._service_name = service_name
        self._method_name = method_name
        self._server = root_url

    def __call__(self, *args, **kwargs):
        """
        Actually calls the real method
        """
        call_started.send(sender=self, service=self._service_name, method=self._method_name, args=args, kwargs=kwargs)

        try:
            raw = self._client.root.call(self._service_name, self._method_name, pickle.dumps((args, kwargs)))
            result = pickle.loads(raw)
        except Exception:
            raise

        call_finished.send(sender=self, result=result)
        return result


class RpycServiceProxy(ServiceProxy):
    """
    JSON RPC
    """
    def __init__(self, name, **kwargs):
        super(RpycServiceProxy, self).__init__(name, **kwargs)
        self._invocations = {}
        self.root_url = kwargs['url']

        # connect
        host, port = tuple(kwargs['url'].split(':'))
        self._client = rpyc.connect(host, int(port))

    def __getattr__(self, method_name):
        if not method_name in self._invocations:
            self._invocations[method_name] = RpycServiceInvocation(self._client, self.name, method_name, self.root_url)

        return self._invocations[method_name].__call__
