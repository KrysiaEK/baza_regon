from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from .forms import SearchForm


class SearchFormView(FormView):
    template_name = 'searcher/form_view.html'
    form_class = SearchForm
    success_url = 'result'

class ResultView(TemplateView):
    template_name = 'searcher/result.html'
