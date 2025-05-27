from abc import abstractmethod


class URLCenter(object):
    @abstractmethod
    def refresh(self, host: str):
        pass
