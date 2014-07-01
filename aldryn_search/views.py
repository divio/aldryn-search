# -*- coding: utf-8 -*-

from django.conf import settings
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView

from haystack.forms import ModelSearchForm
from haystack.query import EmptySearchQuerySet

from .contrib.pagination import DiggPaginator


class AldrynSearchView(FormMixin, ListView):
    template_name = 'aldryn_search/search_results.html'
    queryset = EmptySearchQuerySet()
    form_class = ModelSearchForm
    load_all = False
    searchqueryset = None
    paginate_by = getattr(settings, 'ALDRYN_SEARCH_PAGINATION', 10)
    paginator_class = DiggPaginator

    def get_form_kwargs(self):
        kwargs = super(AldrynSearchView, self).get_form_kwargs()
        kwargs['load_all'] = self.load_all
        if self.searchqueryset is not None:
            kwargs['searchqueryset'] = self.searchqueryset
        return kwargs

    def get_form(self, form_class):
        data = self.request.GET if len(self.request.GET) else None
        return form_class(data, **self.get_form_kwargs())

    def get_query(self, form):
        """
        Returns the query provided by the user.

        Returns an empty string if the query is invalid.
        """
        if form.is_valid():
            return form.cleaned_data['q']
        return ''

    def get(self, request, *args, **kwargs):
        self.form = self.get_form(self.get_form_class())
        return super(AldrynSearchView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return self.form.search()

    def get_context_data(self, **kwargs):
        context = super(AldrynSearchView, self).get_context_data(**kwargs)
        context['query'] = self.get_query(self.form)
        context['form'] = self.form
        results = context['object_list']
        if results and hasattr(results, 'query') and results.query.backend.include_spelling:
            context['suggestion'] = self.form.get_suggestion()
        return context
