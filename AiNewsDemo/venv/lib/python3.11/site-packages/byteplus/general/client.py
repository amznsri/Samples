from datetime import datetime

import logging
from optparse import Option
from typing import Optional

from byteplus.common.client import CommonClient
from byteplus.common.protocol import *
from byteplus.core import BizException
from byteplus.core import MAX_IMPORT_ITEM_COUNT
from byteplus.core import Region
from byteplus.core.context import Param
from byteplus.core.host_availabler import Config
from byteplus.core.metrics.metrics_option import MetricsCfg
from byteplus.general.url import _GeneralURL
from byteplus.general.protocol import *

log = logging.getLogger(__name__)

_ERR_MSG_TOO_MANY_ITEMS = "Only can receive max to {} items in one request".format(MAX_IMPORT_ITEM_COUNT)


class Client(CommonClient):

    def __init__(self, param: Param):
        super().__init__(param)
        self._general_url: _GeneralURL = _GeneralURL(self._context)

    def do_refresh(self, host: str):
        self._general_url.refresh(host)

    def write_data(self, data_list: list, topic: str, *opts: Option) -> WriteResponse:
        if len(data_list) > MAX_IMPORT_ITEM_COUNT:
            raise BizException(_ERR_MSG_TOO_MANY_ITEMS)
        url_format: str = self._general_url.write_data_url_format
        url: str = url_format.replace("#", topic)
        response: WriteResponse = WriteResponse()
        self._http_caller.do_json_request(url, data_list, response, *opts)
        log.debug("[ByteplusSDK][WriteData] rsp:\n %s", response)
        return response

    def predict(self, request: PredictRequest, scene: str, *opts: Option) -> PredictResponse:
        url_format: str = self._general_url.predict_url_format
        url: str = url_format.replace("#", scene)
        response: PredictResponse = PredictResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][Predict] rsp:\n%s", response)
        return response

    def callback(self, request: CallbackRequest, *opts: Option) -> CallbackResponse:
        url: str = self._general_url.callback_url
        response: CallbackResponse = CallbackResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][Callback] rsp:\n%s", response)
        return response


class ClientBuilder(object):
    def __init__(self):
        self._param = Param()

    def tenant(self, tenant: str):
        self._param.tenant = tenant
        return self

    def tenant_id(self, tenant_id: str):
        self._param.tenant_id = tenant_id
        return self

    def token(self, token: str):
        self._param.token = token
        return self

    def schema(self, schema: str):
        self._param.schema = schema
        return self

    def hosts(self, hosts: list):
        self._param.hosts = hosts
        return self

    def headers(self, headers: dict):
        self._param.headers = headers
        return self

    def region(self, region: Region):
        self._param.region = region
        return self

    def metrics_config(self, metrics_config: MetricsCfg):
        self._param.metrics_cfg = metrics_config
        return self

    def host_availabler_config(self, host_availabler_config: Config):
        self._param.host_availabler_config = host_availabler_config
        return self

    def build(self) -> Client:
        self._param.use_air_auth = True
        return Client(self._param)
