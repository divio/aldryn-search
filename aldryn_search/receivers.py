# -*- coding: utf-8 -*-
'''
Created on Nov 30, 2015

@author: jakob
'''
from cms.models.titlemodels import Title
from cms.signals import post_unpublish as post_unpublish_page
from django.dispatch.dispatcher import receiver

from aldryn_search.signals import post_unpublish


@receiver(post_unpublish_page, dispatch_uid='unpublish_title')
def on_post_unpublish_page(sender, instance, language, **kwargs):
    title = instance.publisher_public.get_title_obj(language)
    post_unpublish.send(sender=Title, instance=title)