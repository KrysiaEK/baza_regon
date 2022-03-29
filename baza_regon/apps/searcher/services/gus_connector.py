from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests.exceptions import ConnectionError

import xmltodict

from baza_regon.apps.searcher.exceptions import LengthError, WrongNumberError, WrongTypeError, NotNumberError, \
    WrongKeyError, NoConnectionError
from baza_regon.apps.searcher.constants import GUSnumbers
from baza_regon.settings import GUS_KEY, wsdl


class GUSConnector:
    """Class to connect GUS API and request data"""

    wsdl = wsdl
    report_types = {  # dict with types of business activity and their keys in GUS database to get detailed information
        'F': {
            '1': 'PublDaneRaportDzialalnoscFizycznejCeidg',
            '2': 'PublDaneRaportDzialalnoscFizycznejRolnicza',
            '3': 'PublDaneRaportDzialalnoscFizycznejPozostala',
            '4': 'PublDaneRaportDzialalnoscFizycznejWKrupgn'},
        'LF': 'PublDaneRaportLokalnaFizycznej',
        'P': 'PublDaneRaportPrawna',
        'LP': 'PublDaneRaportLokalnaPrawnej'}

    def __init__(self, type_of_number, number):
        self.type_of_number = type_of_number
        self.number = number
        self.client = self.connect()
        self.validate_number_length()
        self.validate_type()
        self.validate_is_number()

    def connect(self):
        """Function creates session with private key and obtain http header (sid) necessary to send requests"""

        session = Session()
        transport = Transport(session=session)
        try:
            client = Client(wsdl=self.wsdl, transport=transport)
            sid = client.service.Zaloguj(pKluczUzytkownika=GUS_KEY)
            if sid is None:
                raise WrongKeyError
            transport.session.headers.update({"sid": sid})
            return client
        except ConnectionError:
            raise NoConnectionError

    def get_all_important_data(self):
        """Function sends request to GUS database.
        Sends request with number and checks if it exists in database. Converts obtained data to dict. Obtains type of
        report necessary to get more detailed report about organization and sends new request with it. Returns basic
        data and more detailed report"""

        result = self.client.service.DaneSzukajPodmioty(pParametryWyszukiwania={self.type_of_number: str(self.number)})
        if self.client.service.GetValue("KomunikatKod") == '4':
            raise WrongNumberError
        elif self.type_of_number == GUSnumbers.KRS:
            for el in xmltodict.parse(result)['root']['dane']:
                data = dict(el)
        else:
            data = dict(xmltodict.parse(result)['root']['dane'])
        type_of_report = data['Typ']
        if type_of_report in self.report_types.keys() and type_of_report != 'F':
            nr_type = self.report_types[type_of_report]
        else:
            silos_id = data['SilosID']
            nr_type = self.report_types['F'][silos_id]
        regon = data[GUSnumbers.REGON]
        result_of_report = self.client.service.DanePobierzPelnyRaport(pRegon=regon, pNazwaRaportu=nr_type)
        report = dict(xmltodict.parse(result_of_report)['root']['dane'])
        return data, report

    def validate_type(self):
        """Validation of type of number"""

        if self.type_of_number not in GUSnumbers.ALL:
            raise WrongTypeError

    def validate_number_length(self):
        """Validation of number's length"""

        if self.type_of_number == GUSnumbers.REGON and len(self.number) != 9 and len(self.number) != 14:
            raise LengthError
        elif (self.type_of_number == GUSnumbers.KRS or self.type_of_number == GUSnumbers.NIP) and len(
                self.number) != 10:
            raise LengthError

    def validate_is_number(self):
        """Validation if input is number"""

        if not self.number.isnumeric():
            raise NotNumberError
