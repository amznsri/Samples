import datetime
from abc import abstractmethod

from byteplus.core.options import Options


class Option(object):
    @abstractmethod
    def fill(self, options: Options) -> None:
        raise NotImplementedError

    @staticmethod
    def conv_to_options(opts: tuple) -> Options:
        options: Options = Options()
        for opt in opts:
            opt.fill(options)
        return options

    @staticmethod
    def with_timeout(timeout: datetime.timedelta):
        class OptionImpl(Option):
            def fill(self, options: Options) -> None:
                options.timeout = timeout

        return OptionImpl()

    @staticmethod
    def with_request_id(request_id: str):
        class OptionImpl(Option):
            def fill(self, options: Options) -> None:
                options.request_id = request_id

        return OptionImpl()

    @staticmethod
    def with_headers(headers: dict):
        class OptionImpl(Option):
            def fill(self, options: Options) -> None:
                options.headers = headers

        return OptionImpl()

    @staticmethod
    def with_data_date(date: datetime.datetime):
        class OptionImpl(Option):
            def fill(self, options: Options) -> None:
                options.data_date = date

        return OptionImpl()

    @staticmethod
    def with_data_end(end: bool):
        class OptionImpl(Option):
            def fill(self, options: Options) -> None:
                options.date_end = end

        return OptionImpl()

    @staticmethod
    def with_server_timeout(timeout: datetime.timedelta):
        class OptionImpl(Option):
            def fill(self, options: Options) -> None:
                options.server_timeout = timeout

        return OptionImpl()

    @staticmethod
    def with_queries(queries: dict):
        class OptionImpl(Option):
            def fill(self, options: Options) -> None:
                options.queries = queries

        return OptionImpl()

    @staticmethod
    def with_stage(stage: str):
        class OptionImpl(Option):
            def fill(self, options: Options) -> None:
                options.stage = stage

        return OptionImpl()

    @staticmethod
    def with_scene(scene: str):
        class OptionImpl(Option):
            def fill(self, options: Options) -> None:
                options.scene = scene

        return OptionImpl()