_DEFAULT_WINDOW_SIZE: int = 60
_DEFAULT_PING_URL_FORMAT: str = "#://{}/predict/api/ping"
_DEFAULT_PING_TIMEOUT_SECONDS: float = 0.3
_DEFAULT_PING_INTERVAL_SECONDS: float = 1


class Config(object):
    def __init__(self,
                 ping_url_format: str = _DEFAULT_PING_URL_FORMAT,
                 window_size: int = _DEFAULT_WINDOW_SIZE,
                 ping_timeout_seconds: float = _DEFAULT_PING_TIMEOUT_SECONDS,
                 ping_interval_seconds: float = _DEFAULT_PING_INTERVAL_SECONDS):
        self.ping_url_format = ping_url_format
        self.window_size = window_size
        if window_size < 0:
            self.window_size = _DEFAULT_WINDOW_SIZE
        self.ping_timeout_seconds = ping_timeout_seconds
        self.ping_interval_seconds = ping_interval_seconds
