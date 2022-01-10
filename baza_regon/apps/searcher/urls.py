from django.urls import path
from . import views
app_name = 'searcher'

urlpatterns = [
    path('search', views.SearchFormView.as_view(), name='search'),
    path('result', views.ResultView.as_view(), name='result'),
]
