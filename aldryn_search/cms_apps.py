from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from .conf import settings


class AldrynSearchApphook(CMSApp):
    name = _("aldryn search")
    urls = ['aldryn_search.urls']

    def get_urls(self, *args, **kwargs):
        return self.urls


if settings.ALDRYN_SEARCH_REGISTER_APPHOOK:
    apphook_pool.register(AldrynSearchApphook)
