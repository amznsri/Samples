import logging
from optparse import Option

from byteplus.common.client import CommonClient
from byteplus.common.protocol import *
from byteplus.core import BizException
from byteplus.core import MAX_WRITE_ITEM_COUNT, MAX_IMPORT_ITEM_COUNT
from byteplus.core import Region
from byteplus.core.context import Param
from byteplus.core.host_availabler import Config
from byteplus.core.metrics.metrics_option import MetricsCfg
from byteplus.retail.protocol import *
from byteplus.retail.url import _RetailURL

log = logging.getLogger(__name__)

_TOO_MANY_WRITE_ITEMS_ERR_MSG = "Only can receive {} items in one write request".format(MAX_WRITE_ITEM_COUNT)
_TOO_MANY_IMPORT_ITEMS_ERR_MSG = "Only can receive {} items in one import request".format(MAX_IMPORT_ITEM_COUNT)


class Client(CommonClient):

    def __init__(self, param: Param):
        super().__init__(param)
        self._retail_url: _RetailURL = _RetailURL(self._context)

    def do_refresh(self, host: str):
        self._retail_url.refresh(host)

    def write_users(self, request: WriteUsersRequest, *opts: Option) -> WriteUsersResponse:
        if len(request.users) > MAX_WRITE_ITEM_COUNT:
            raise BizException(_TOO_MANY_WRITE_ITEMS_ERR_MSG)
        url: str = self._retail_url.write_users_url
        response: WriteUsersResponse = WriteUsersResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][WriteUsers] rsp:\n %s", response)
        return response

    def import_users(self, request: ImportUsersRequest, *opts: Option) -> OperationResponse:
        if len(request.input_config.users_inline_source.users) > MAX_IMPORT_ITEM_COUNT:
            raise BizException(_TOO_MANY_IMPORT_ITEMS_ERR_MSG)
        url: str = self._retail_url.import_users_url
        response: OperationResponse = OperationResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][ImportUsers] rsp:\n%s", response)
        return response

    def write_products(self, request: WriteProductsRequest, *opts: Option) -> WriteProductsResponse:
        if len(request.products) > MAX_WRITE_ITEM_COUNT:
            raise BizException(_TOO_MANY_WRITE_ITEMS_ERR_MSG)
        url: str = self._retail_url.write_products_url
        response: WriteProductsResponse = WriteProductsResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][WriteProducts] rsp:\n %s", response)
        return response

    def import_products(self, request: ImportProductsRequest, *opts: Option) -> OperationResponse:
        if len(request.input_config.products_inline_source.products) > MAX_IMPORT_ITEM_COUNT:
            raise BizException(_TOO_MANY_IMPORT_ITEMS_ERR_MSG)
        url: str = self._retail_url.import_products_url
        response: OperationResponse = OperationResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][ImportProducts] rsp:\n%s", response)
        return response

    def write_user_events(self, request: WriteUserEventsRequest, *opts: Option) -> WriteUserEventsResponse:
        if len(request.user_events) > MAX_WRITE_ITEM_COUNT:
            raise BizException(_TOO_MANY_WRITE_ITEMS_ERR_MSG)
        url: str = self._retail_url.write_user_events_url
        response: WriteUserEventsResponse = WriteUserEventsResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][WriteUserEvents] rsp:\n %s", response)
        return response

    def import_user_events(self, request: ImportUserEventsRequest, *opts: Option) -> OperationResponse:
        if len(request.input_config.user_events_inline_source.user_events) > MAX_IMPORT_ITEM_COUNT:
            raise BizException(_TOO_MANY_IMPORT_ITEMS_ERR_MSG)
        url: str = self._retail_url.import_user_events_url
        response: OperationResponse = OperationResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][ImportUserEvents] rsp:\n%s", response)
        return response

    def predict(self, request: PredictRequest, scene: str, *opts: Option) -> PredictResponse:
        url_format: str = self._retail_url.predict_url_format
        url: str = url_format.replace("#", scene)
        response: PredictResponse = PredictResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][Predict] rsp:\n%s", response)
        return response

    def ack_server_impressions(self, request: AckServerImpressionsRequest,
                               *opts: Option) -> AckServerImpressionsResponse:
        url: str = self._retail_url.ack_impression_url
        response: AckServerImpressionsResponse = AckServerImpressionsResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][AckImpressions] rsp:\n%s", response)
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
