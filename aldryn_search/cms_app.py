from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from aldryn_search.views import AldrynSearchView

from .conf import settings


class AldrynSearchApphook(CMSApp):
    name = _("aldryn search")
    urls = [
        patterns(
            '',
            url('^$', AldrynSearchView.as_view(), name='aldryn-search'),
        )
    ]


if settings.ALDRYN_SEARCH_REGISTER_APPHOOK:
    apphook_pool.register(AldrynSearchApphook)
