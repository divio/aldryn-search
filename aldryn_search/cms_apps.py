from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from .conf import settings


@apphook_pool.register
class AldrynSearchApphook(CMSApp):
    name = _("Aldryn Search")
    app_name = "aldryn_search"
    
    def get_urls(self, page=None, language=None, **kwargs):
        return ["aldryn_search.urls"]  

    @property
    def urls(self):
        return self.get_urls()
