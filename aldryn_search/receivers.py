# -*- coding: utf-8 -*-
'''
Created on Nov 30, 2015
@author: jakob
'''
from django.dispatch.dispatcher import receiver

from cms.models.titlemodels import Title
from cms.signals import post_unpublish as post_unpublish_page

from .signals import remove_from_index


@receiver(post_unpublish_page, dispatch_uid='unpublish_cms_page')
def unpublish_cms_page(sender, instance, language, **kwargs):
    title = instance.publisher_public.get_title_obj(language)
    remove_from_index.send(sender=Title, instance=title)
