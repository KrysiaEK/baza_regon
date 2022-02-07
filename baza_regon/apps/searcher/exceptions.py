from rest_framework import exceptions, status


class WrongTypeError(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Podany typ numeru nie istnieje. Spróbuj zacząć od wielkiej litery"


class LengthError(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Podany numer posiada niewłaściwą liczbę znaków"


class NotNumberError(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Podane dane nie są numerem"


class WrongNumberError(exceptions.APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Podany numer jest niepoprawny"
