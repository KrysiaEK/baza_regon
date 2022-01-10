from django import forms


class SearchForm(forms.Form):
    regon = forms.CharField(label='REGON', max_length=9, min_length=9, required=False)
    nip = forms.CharField(label='NIP', max_length=10, min_length=10, required=False)
    krs = forms.CharField(label='KRS', max_length=10, min_length=10, required=False)

