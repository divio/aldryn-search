# -*- coding: utf-8 -*-
'''
Created on Nov 30, 2015

@author: jakob
'''
from django.dispatch.dispatcher import Signal

add_to_index = Signal(providing_args=['instance', 'object_action'])
remove_from_index = Signal(providing_args=['instance', 'object_action'])
