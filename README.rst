django-default-filter
================

When visiting django admin changelist page, apply a default admin list filter. 
For example, you arrive at /admin/cms/page/?status=active when you visit the changelist for Page. 

Quickstart
----------

::

    pip install django-default-filter

Add this to your settings file:

::

    MIDDLEWARE_CLASSES = [
        'django_default_filter.default_filter.DefaultFilterMiddleware',
    ]
    
    ADMIN_DEFAULT_CHANGELIST_FILTERS = {
        "/admin/cms/page/": {
            "query": "status",
            "value": "active",
        }
    }
