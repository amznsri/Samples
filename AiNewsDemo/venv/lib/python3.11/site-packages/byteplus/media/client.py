import logging

from byteplus.common.client import CommonClient
from byteplus.core import Region, Option, MAX_WRITE_ITEM_COUNT, BizException
from byteplus.core.context import Param
from byteplus.core.host_availabler import Config
from byteplus.core.metrics.metrics_option import MetricsCfg
from byteplus.media.protocol import WriteUsersRequest, WriteUsersResponse, WriteContentsRequest, WriteContentsResponse, \
    WriteUserEventsRequest, WriteUserEventsResponse, PredictRequest, PredictResponse, AckServerImpressionsRequest, \
    AckServerImpressionsResponse
from byteplus.media.url import _MediaURL

log = logging.getLogger(__name__)

_TOO_MANY_WRITE_ITEMS_ERR_MSG = "Only can receive {} items in one write request".format(MAX_WRITE_ITEM_COUNT)


class Client(CommonClient):

    def __init__(self, param: Param):
        super().__init__(param)
        self._media_url: _MediaURL = _MediaURL(self._context)

    def do_refresh(self, host: str):
        self._media_url.refresh(host)

    def write_users(self, request: WriteUsersRequest, *opts: Option) -> WriteUsersResponse:
        if len(request.users) > MAX_WRITE_ITEM_COUNT:
            raise BizException(_TOO_MANY_WRITE_ITEMS_ERR_MSG)
        url: str = self._media_url.write_users_url
        response: WriteUsersResponse = WriteUsersResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][WriteUsers] rsp:\n %s", response)
        return response

    def write_contents(self, request: WriteContentsRequest, *opts: Option) -> WriteContentsResponse:
        if len(request.contents) > MAX_WRITE_ITEM_COUNT:
            raise BizException(_TOO_MANY_WRITE_ITEMS_ERR_MSG)
        url: str = self._media_url.write_contents_url
        response: WriteContentsResponse = WriteContentsResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][WriteContents] rsp:\n %s", response)
        return response

    def write_user_events(self, request: WriteUserEventsRequest, *opts: Option) -> WriteUserEventsResponse:
        if len(request.user_events) > MAX_WRITE_ITEM_COUNT:
            raise BizException(_TOO_MANY_WRITE_ITEMS_ERR_MSG)
        url: str = self._media_url.write_user_events_url
        response: WriteUserEventsResponse = WriteUserEventsResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][WriteUserEvents] rsp:\n %s", response)
        return response

    def predict(self, request: PredictRequest, scene: str, *opts: Option) -> PredictResponse:
        url_format: str = self._media_url.predict_url_format
        url: str = url_format.replace("#", scene)
        response: PredictResponse = PredictResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][Predict] rsp:\n%s", response)
        return response

    def ack_server_impressions(self, request: AckServerImpressionsRequest,
                               *opts: Option) -> AckServerImpressionsResponse:
        url: str = self._media_url.ack_impression_url
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
