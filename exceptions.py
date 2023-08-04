class NoSendMessage(Exception):
    """Ошибка отправки сообщения."""

    pass


class ConnectApiError(Exception):
    """Ошибка соединенеия с API."""

    pass


class InvalidRequest(Exception):
    """Ошибка в получении запроса."""

    pass


class UnknownStatus(Exception):
    """Hеизвестный статус работы."""

    pass
