from django import forms

from zeep import Client


class SearchForm(forms.Form):
    regon = forms.CharField(label='REGON', max_length=14, min_length=9, required=False)
    nip = forms.CharField(label='NIP', max_length=10, min_length=10, required=False)
    krs = forms.CharField(label='KRS', max_length=10, min_length=10, required=False)


class DetailsForm(forms.Form):
    regon = forms.CharField(label='REGON', max_length=14, min_length=9, required=True)
    report_name = forms.CharField(label='nazwa_raportu', max_length=14, min_length=9, required=True)




