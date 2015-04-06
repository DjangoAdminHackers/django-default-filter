import sys

from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class DefaultFilterMiddleware(object):
    def process_request(self, request):
        # This middleware is not for admin only
        if not request.user.is_staff:
            return None

        if not (request.path.startswith(reverse('admin:index'))):
            return None

        default_filters = getattr(settings, 'ADMIN_DEFAULT_CHANGELIST_FILTERS', {})

        # we have to do this if check, or the user is never able to select "All" of this list_filter
        referer = request.META.get('HTTP_REFERER', '')
        if referer and referer.count(request.get_full_path()):
            return None
        

        if request.get_full_path() in default_filters.keys():
            
            filter = default_filters.get(request.path)
            query = filter['query']

            if 'callback' in filter:
                callback_module = __import__(filter['callback'])
                callback = sys.modules[filter['callback']]
                value = callback.get_defaults(query)
            elif 'value' in filter:
                value = filter['value']
            return HttpResponseRedirect('%s?%s=%s' % (request.path, query, value) )
