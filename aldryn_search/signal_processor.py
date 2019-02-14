# -*- coding: utf-8 -*-
'''
Created on Dec 1, 2015

@author: jakob
'''
import copy

from haystack.exceptions import NotHandled
from haystack.signals import \
    RealtimeSignalProcessor as BaseRealtimeSignalProcessor

from .signals import add_to_index, remove_from_index


class RealtimeSignalProcessor(BaseRealtimeSignalProcessor):

    def setup(self):
        super(RealtimeSignalProcessor, self).setup()
        add_to_index.connect(self.handle_save)
        remove_from_index.connect(self.handle_delete)

    def teardown(self):
        super(RealtimeSignalProcessor, self).teardown()
        add_to_index.disconnect(self.handle_save)
        remove_from_index.disconnect(self.handle_delete)

    def handle_save(self, sender, instance, **kwargs):
        kwargs = copy.copy(kwargs)

        # Exact copy of Haystack's handle_save()
        # except that we pass any kwargs to the update_object method
        using_backends = self.connection_router.for_write(instance=instance)

        for using in using_backends:
            kwargs['using'] = using

            try:
                index = self.connections[using].get_unified_index().get_index(sender)
                # TODO: This should be done by haystack.
                index.update_object(instance, **kwargs)
            except NotHandled:
                # TODO: Maybe log it or let the exception bubble?
                pass
