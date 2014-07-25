# -*- coding: utf-8 -*-
from django.utils.translation import get_language_from_request
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from haystack.forms import ModelSearchForm
from haystack.query import SearchQuerySet

from aldryn_common.paginator import DiggPaginator

from .conf import settings
from .utils import alias_from_language, get_model_path


class AldrynSearchView(FormMixin, ListView):
    form_class = ModelSearchForm

    # A list of models to limit search by.
    # Only indexes registered to these models will be searched.
    models = None

    load_all = False

    paginate_by = settings.ALDRYN_SEARCH_PAGINATION
    paginator_class = DiggPaginator

    # SearchQueryset instance to use for querying
    search_queryset = None
    # SearchQueryset class to instantiate if no search_queryset instance is defined.
    search_queryset_class = SearchQuerySet

    template_name = 'aldryn_search/search_results.html'

    def get_form_kwargs(self):
        kwargs = super(AldrynSearchView, self).get_form_kwargs()
        kwargs['load_all'] = self.load_all
        kwargs['searchqueryset'] = self.get_search_queryset()

        data = self.request.GET

        if self.models:
            data = data.copy()
            data.setlist('models', (get_model_path(model) for model in self.models))
        kwargs['data'] = data
        return kwargs

    def get_query(self, form):
        """
        Returns the query provided by the user.

        Returns an empty string if the query is invalid.
        """
        if form.is_valid():
            return form.cleaned_data['q']
        return ''

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)
        return super(AldrynSearchView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.form.search()
        if not self.request.user.is_authenticated():
            queryset = queryset.exclude(login_required=True)
        return queryset

    def get_search_queryset(self):
        if self.search_queryset is None:
            language = get_language_from_request(self.request, check_path=True)
            connection_alias = alias_from_language(language)
            return self.search_queryset_class(using=connection_alias)
        return self.search_queryset

    def get_context_data(self, **kwargs):
        context = super(AldrynSearchView, self).get_context_data(**kwargs)
        context['query'] = self.get_query(self.form)
        context['form'] = self.form
        results = context['object_list']
        if results and hasattr(results, 'query') and results.query.backend.include_spelling:
            context['suggestion'] = self.form.get_suggestion()
        return context
