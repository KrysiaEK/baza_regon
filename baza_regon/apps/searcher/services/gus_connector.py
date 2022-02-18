from zeep import Client
from zeep.transports import Transport
from requests import Session

import xmltodict

from baza_regon.apps.searcher.exceptions import LengthError, WrongNumberError, WrongTypeError, NotNumberError


class GUSConnector:

    """Class to connect GUS API and request data"""

    wsdl = 'https://wyszukiwarkaregontest.stat.gov.pl/wsBIR/wsdl/UslugaBIRzewnPubl-ver11-test.wsdl'
    report_types = {
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
        client = Client(wsdl=self.wsdl, transport=transport)
        sid = client.service.Zaloguj(pKluczUzytkownika="abcde12345abcde12345")
        transport.session.headers.update({"sid": sid})
        return client

    def get_all_important_data(self):

        """Function sends request to GUS database

        Sends request with number and checks if it exists in database. Converts obtained data to dict. Obtains type of
        report necessary to get more detailed report about organization and sends new request with it. Returns basic
        data and more detailed report"""

        result = self.client.service.DaneSzukajPodmioty(pParametryWyszukiwania={self.type_of_number: str(self.number)})
        if 'Nie znaleziono podmiotu dla podanych kryteriów wyszukiwania.' in result:
            raise WrongNumberError
        if self.type_of_number == 'Krs':
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
        regon = data['Regon']
        result_of_report = self.client.service.DanePobierzPelnyRaport(pRegon=regon, pNazwaRaportu=nr_type)
        report = dict(xmltodict.parse(result_of_report)['root']['dane'])
        return data, report

    def validate_type(self):

        """Validation of type of number"""

        if self.type_of_number not in ['Nip', 'Krs', 'Regon']:
            raise WrongTypeError

    def validate_number_length(self):

        """Validation of number's length"""

        if self.type_of_number == 'Regon' and len(self.number) != 9 and len(self.number) != 14:
            raise LengthError
        elif (self.type_of_number == 'Krs' or self.type_of_number == 'Nip') and len(self.number) != 10:
            raise LengthError

    def validate_is_number(self):

        """Validation if input is number"""

        if not self.number.isnumeric():
            raise NotNumberError
