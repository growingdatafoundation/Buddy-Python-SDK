from datetime import datetime


class AccessToken(object):
    def __init__(self, values):
        if values is None or values is "":
            self._token = ""
            self.__set_expires(None)
        else:
            self._token = values[0]
            self.__set_expires(values[1])

    @property
    def token(self):
        if self._token is None or self._token is "" or self._expires <= datetime.utcnow():
            return None
        else:
            return self._token

    @property
    def expires(self):
        return self._expires

    def __set_expires(self, value):
        if value is None or value is "":
            self._expires = datetime.utcfromtimestamp(0)
        else:
            ticks = int(float(value))
            timestamp = AccessToken.__timestamp_from_ticks(ticks)
            self._expires = datetime.utcfromtimestamp(timestamp)

    @staticmethod
    def __timestamp_from_ticks(ticks):
        return ticks / 1000
