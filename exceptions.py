class ConnectApiError(Exception):
    """Ошибка соединенеия с API."""

    pass


class InvalidRequest(Exception):
    """Ошибка в получении запроса."""

    pass


class UnknownStatus(Exception):
    """Hеизвестный статус работы."""

    pass


class EmptyResponseAPI(Exception):
    """Пустой ответ API."""

    pass
