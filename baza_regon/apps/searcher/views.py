from rest_framework.views import APIView
from rest_framework.response import Response

from baza_regon.apps.searcher.services.gus_connector import GUSConnector


class GUSApiView(APIView):
    """View takes user input and use GUSConnector to find and return data"""

    def get(self, request, *args, **kwargs):
        type_of_nr = request.GET.get('type_of_number')
        nr = request.GET.get('number')
        connector = GUSConnector(type_of_number=type_of_nr, number=nr)
        data = connector.get_all_important_data()
        return Response(data=data)
