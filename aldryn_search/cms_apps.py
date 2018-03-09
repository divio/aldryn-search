from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


from .conf import settings


@apphook_pool.register
class AldrynSearchApphook(CMSApp):
    name = _("aldryn search")
    app_name = 'aldryn-search'
    
    def get_urls(self, page=None, language=None, **kwargs):
        return ['aldryn_search.urls']  
