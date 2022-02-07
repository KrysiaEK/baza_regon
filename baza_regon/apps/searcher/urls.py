from django.urls import path

from baza_regon.apps.searcher.views import GUSApiView


urlpatterns = [
    path('gus_data/', GUSApiView.as_view(), name='get_data')
]
