from cms.models import Page, Title


class TitleProxy(Title):
    class Meta:
        proxy = True
        verbose_name = Page._meta.verbose_name
        verbose_name_plural = Page._meta.verbose_name_plural
