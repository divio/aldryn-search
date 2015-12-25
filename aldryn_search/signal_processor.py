# -*- coding: utf-8 -*-
'''
Created on Dec 1, 2015

@author: jakob
'''
from haystack.signals import RealtimeSignalProcessor

from aldryn_search.signals import add_to_index, remove_from_index


class AldrynSignalProcessor(RealtimeSignalProcessor):
    
    def setup(self):
        super(AldrynSignalProcessor, self).setup()
        add_to_index.connect(self.handle_save)
        remove_from_index.connect(self.handle_delete)

    def teardown(self):
        super(AldrynSignalProcessor, self).teardown()
        add_to_index.disconnect(self.handle_save)
        remove_from_index.disconnect(self.handle_delete)
