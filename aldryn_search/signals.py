# -*- coding: utf-8 -*-
'''
Created on Nov 30, 2015

@author: jakob
'''
from django.dispatch.dispatcher import Signal

post_unpublish = Signal(providing_args=['instance'])