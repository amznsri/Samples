from byteplus.core.context import Context
from byteplus.core.url_center import URLCenter

# The URL format of operation information
# Example: https://tob.sgsnssdk.com/data/api/retail/retail_demo/operation?method=get
_OPERATION_URL_FORMAT = "{}://{}/data/api/{}/operation?method={}"

# The URL format of done information
# Example: https://tob.sgsnssdk.com/data/api/retail/retail_demo/done?topic=user
_DONE_URL_FORMAT = "{}://{}/data/api/{}/done?topic=#"


class CommonURL(URLCenter):
    def __init__(self, context: Context):
        self.schema = context.schema
        self.tenant = context.tenant
        # The URL of getting operation information which is real-time
        # Example: https://tob.sgsnssdk.com/data/api/retail_demo/operation?method=get
        self.get_operation_url: str = ""
        # The URL of query operations information which is non-real-time
        # Example: https://tob.sgsnssdk.com/data/api/retail_demo/operation?method=list
        self.list_operations_url: str = ""
        # The URL of mark certain days that data synchronization is complete
        # Example: https://tob.sgsnssdk.com/data/api/retail_demo/done?topic=user
        self.done_url_format: str = ""
        self.refresh(context.hosts[0])

    def refresh(self, host: str):
        self.get_operation_url: str = self._generate_operation_url(host, "get")
        self.list_operations_url: str = self._generate_operation_url(host, "list")
        self.done_url_format: str = self._generate_done_url(host)

    def _generate_operation_url(self, host, method) -> str:
        return _OPERATION_URL_FORMAT.format(self.schema, host, self.tenant, method)

    def _generate_done_url(self, host) -> str:
        return _DONE_URL_FORMAT.format(self.schema, host, self.tenant)

