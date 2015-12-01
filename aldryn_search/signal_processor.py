# -*- coding: utf-8 -*-
'''
Created on Dec 1, 2015

@author: jakob
'''
from haystack.signals import RealtimeSignalProcessor

from aldryn_search.signals import post_unpublish


class AldrynSignalProcessor(RealtimeSignalProcessor):
    
    def setup(self):
        super(AldrynSignalProcessor, self).setup()
        post_unpublish.connect(self.handle_delete)
        
    def teardown(self):
        super(AldrynSignalProcessor, self).teardown()
        post_unpublish.disconnect(self.handle_delete)