# -*- coding: utf-8 -*-
'''
Created on Nov 30, 2015

@author: jakob
'''
from django.dispatch.dispatcher import Signal
from haystack.signals import RealtimeSignalProcessor


post_unpublish = Signal(providing_args=['instance'])

class AldrynSignalProcessor(RealtimeSignalProcessor):
    
    def setup(self):
        super(AldrynSignalProcessor, self).setup()
        post_unpublish.connect(self.handle_delete)
        
    def teardown(self):
        super(AldrynSignalProcessor, self).teardown()
        post_unpublish.disconnect(self.handle_delete)

