from byteplus.core.constant import _CN_HOSTS, _SG_HOSTS, _US_HOSTS
from byteplus.core.host_availabler_config import Config
from byteplus.core.metrics.metrics_option import MetricsCfg
from byteplus.core.region import Region


class Param(object):
    def __init__(self):
        self.tenant: str = ""
        self.tenant_id: str = ""
        self.token: str = ""
        self.retry_times: int = 0
        self.schema: str = "https"
        self.hosts: list = []
        self.headers: dict = {}
        self.region: Region = Region.UNKNOWN
        self.ak: str = ""
        self.sk: str = ""
        self.use_air_auth: bool = False
        self.metrics_cfg: MetricsCfg = None
        self.host_availabler_config: Config = None


class Context(object):
    def __init__(self, param: Param):
        self._check_required_field(param)
        self.tenant: str = param.tenant
        self.tenant_id: str = param.tenant_id
        self.token: str = param.token
        self.customer_headers: dict = param.headers
        self.schema: str = param.schema
        self.use_air_auth: bool = param.use_air_auth
        self.hosts: list = []
        self.volc_auth_conf: VolcAuthConf = VolcAuthConf(param)
        self.metrics_cfg: MetricsCfg = param.metrics_cfg
        self.host_availabler_config = param.host_availabler_config
        self._adjust_hosts(param)

    @staticmethod
    def _check_required_field(param: Param) -> None:
        if len(param.tenant) == 0:
            raise Exception("Tenant is empty")
        if len(param.tenant_id) == 0:
            raise Exception("Tenant id is emtpy")
        if param.region == Region.UNKNOWN:
            raise Exception("Region is empty")
        Context._check_auth_required_field(param)

    @staticmethod
    def _check_auth_required_field(param: Param) -> None:
        if param.use_air_auth and param.token == "":
            raise Exception("Token is empty")

        if not param.use_air_auth and (param.sk == "" or param.ak == ""):
            raise Exception("Ak or sk is empty")

    def _adjust_hosts(self, param: Param) -> None:
        if len(param.hosts) > 0:
            self.hosts = param.hosts
            return
        if param.region == Region.CN:
            self.hosts = _CN_HOSTS
            return
        if param.region == Region.SG:
            self.hosts = _SG_HOSTS
            return
        if param.region == Region.US:
            self.hosts = _US_HOSTS
            return


class VolcAuthConf(object):
    def __init__(self, param: Param):
        self.ak: str = param.ak
        self.sk: str = param.sk
        self.region: str = self._parse_region(param)

    def _parse_region(self, param: Param):
        if param.region == Region.SG:
            return "ap-singapore-1"
        if param.region == Region.US:
            return "us-east-1"
        return "cn-north-1"
