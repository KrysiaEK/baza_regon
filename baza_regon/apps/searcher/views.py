from django.core.exceptions import ValidationError
from django.views.generic.edit import FormView, View
from django.views.generic import TemplateView
from .forms import SearchForm

import xmltodict

from zeep import Client
from zeep.transports import Transport
from requests import Session


transport = Transport(session=Session())
wsdl = 'https://wyszukiwarkaregontest.stat.gov.pl/wsBIR/wsdl/UslugaBIRzewnPubl-ver11-test.wsdl'
client = Client(wsdl=wsdl, transport=transport)
sid = client.service.Zaloguj(pKluczUzytkownika="abcde12345abcde12345")
transport.session.headers.update({"sid": sid})


class SearchFormView(FormView, View):
    template_name = 'searcher/form_view.html'
    form_class = SearchForm
    success_url = 'result'

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        if not form.is_valid():
            raise ValidationError('Niepoprawne dane')
        if form.cleaned_data['nip'] != "":
            type = "Nip"
            number = form.cleaned_data['nip']
        elif form.cleaned_data['krs'] != "":
            type = "Krs"
            number = form.cleaned_data['krs']
        elif form.cleaned_data['regon'] != "":
            type = "Regon"
            number = form.cleaned_data['regon']
        search_parameter = {type: str(number)}
        result = client.service.DaneSzukajPodmioty(pParametryWyszukiwania=search_parameter)
        if form.cleaned_data['krs'] != "":
            for el in xmltodict.parse(result)['root']['dane']:
                data = dict(el)
        else:
            data = dict(xmltodict.parse(result)['root']['dane'])
        type_of_report = data['Typ']
        print(type_of_report)
        return super().form_valid(form)



class ResultView(TemplateView):
    template_name = 'searcher/result.html'


class DetailView(View):
    template_name = 'searcher/detail.html'
    report_types = {
        'F': {
            '1': 'PublDaneRaportDzialalnoscFizycznejCeidg',
            '2': 'PublDaneRaportDzialalnoscFizycznejRolnicza',
            '3': 'PublDaneRaportDzialalnoscFizycznejPozostala',
            '4': 'PublDaneRaportDzialalnoscFizycznejWKrupgn'},
        'LF': 'PublDaneRaportLokalnaFizycznej',
        'P': 'PublDaneRaportPrawna',
        'LP': 'PublDaneRaportLokalnaPrawnej'}

    result = client.service.DanePobierzPelnyRaport(pRegon='180913100', pNazwaRaportu='PublDaneRaportDzialalnoscFizycznejCeidg')
    data = dict(xmltodict.parse(result)['root']['dane'])

