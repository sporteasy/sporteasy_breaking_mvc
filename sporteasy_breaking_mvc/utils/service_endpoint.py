import inspect
import re
from django.core.urlresolvers import reverse

ALL_SERVICES = "all"


class ServiceEndpoint(object):
    """Endpoint service class"""

    def _all_get_methods(self):
        """Return all methods"""
        return [method_tuple[0] for method_tuple in inspect.getmembers(
            self.__class__, predicate=inspect.ismethod)]

    def _clean_available_methods(self, methods):
        """Return services list without internal methods"""

        temp_methods = list(methods)    # copy
        for reg_ex in [
                'available_get_methods',
                'available_post_methods',
                'available_put_methods',
                'available_delete_methods',
                'get_required_method_args',
                "^_"]:
            regex = re.compile(reg_ex)

            for method in methods:
                if regex.findall(method) and method in temp_methods:
                    temp_methods.remove(method)

        #Add discover method:
        if not 'discover' in temp_methods:
            temp_methods.append('discover')
        return temp_methods

    # pylint: disable=E1101
    def available_get_methods(self):
        """Return GET services list, callable by API"""

        if '_get_methods' in self.__dict__.keys():
            if ALL_SERVICES in self._get_methods:
                methods = self._all_get_methods()
            else:
                methods = self._get_methods
        else:
            methods = self._all_get_methods()   # Default if undefined

        return self._clean_available_methods(methods)

    def available_post_methods(self):
        """Return POST services list, callable by API"""
        return self._clean_available_methods([])

    def available_put_methods(self):
        """Return PUT services list, callable by API"""
        return self._clean_available_methods([])

    def available_delete_methods(self):
        """Return DELETE services list, callable by API"""
        return self._clean_available_methods([])

    def discover(self, **request):
        """Return all available service"""

        if request['http_request'] == 'GET':
            methods = self._all_get_methods()
        elif request['http_request'] == 'POST':
            methods = self.available_post_methods()
        else:
            methods = []

        method_call = '?method=' + request['root_name'] + '.' + \
            request['service_name'] + '.'

        return {'methods': self._clean_available_methods(methods),
                'url': reverse('service-view') + method_call}

    def get_required_method_args(self, method_name):
        """Return required arguments for method"""

        list_args = inspect.getargspec(getattr(self, method_name))[0]
        list_args.remove('self')
        return list_args
