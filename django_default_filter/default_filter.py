import sys

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse

class DefaultFilterMiddleware(object):
    def process_request(self, request):
        # This middleware is not for admin only
        if not request.user.is_staff:
            return None

        if not (request.path.startswith(reverse('admin:index'))):
            return None

        default_filters = getattr(settings, 'ADMIN_DEFAULT_CHANGELIST_FILTERS', {})
        
        referer = request.META.get('HTTP_REFERER', '')
        #see if this request has default filter rules. 
        if request.path in default_filters.keys():
            
            # When referer is available, and it is about current model. 
            if referer and referer.count(request.get_full_path()):
                #see if we remembered the query string 
                if self.get_query(request):
                    target = '%s?%s' % (request.path, self.get_query(request))
                    # avoid redirect loop. 
                    if target == request.get_full_path():
                        return None

                    #if user has touched other filter queries, do not redirect
                    if request.META.get('QUERY_STRING', ''):
                        return None
                    
                    absolute_target = request.build_absolute_uri(target)
                    # The remembered query is the same as where the user comes from. 
                    # We need this or user won't be able to go from ?key=val to ? 
                    if absolute_target == referer or referer == request.build_absolute_uri():
                        return None
                    
                    # redirect to the remembered query string
                    return HttpResponseRedirect(target)
            
            # get settings for this request
            filter = default_filters.get(request.path)
            query = filter['query']
            if 'callback' in filter:
                callback_module = __import__(filter['callback'])
                callback = sys.modules[filter['callback']]
                value = callback.get_defaults(query)
            elif 'value' in filter:
                value = filter['value']
            target = '%s?%s=%s' % (request.path, query, value)
            absolute_target = request.build_absolute_uri(target)

            #remember the current query string, if it's not empty
            if request.GET.get(query, None):
                query_string = '%s=%s' % (query, request.GET[query])
                if query_string:
                    #and do not remember other queries
                    self.remember_query(request, query_string)
                    return None
            
            #if user has touched other filter queries, do not redirect
            if request.META.get('QUERY_STRING', ''):
                return None

            # do not redirect if user is trying to click away from ?query=val
            if absolute_target == referer:
                return None
            
            # do the redirect. 
            return HttpResponseRedirect(target)
    
    def remember_query(self, request, query):
        request.session['path_queries'] = request.session.get('path_queries', {})
        request.session['path_queries'].update({request.path: query})
        
    def get_query(self, request):
        request.session['path_queries'] = request.session.get('path_queries', {})
        return request.session['path_queries'].get(request.path, None) 
    