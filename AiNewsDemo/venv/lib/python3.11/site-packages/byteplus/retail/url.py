from byteplus.common.url import CommonURL
from byteplus.core.context import Context

# The URL template of "predict" request, which need fill with "scene" info when use
# Example: https://tob.sgsnssdk.com/predict/api/retail/demo/home
_PREDICT_URL_FORMAT = "{}://{}/predict/api/retail/{}/#"

# The URL format of reporting the real exposure list
# Example: https://tob.sgsnssdk.com/predict/api/retail/demo/ack_impression
_ACK_IMPRESSION_URL_FORMAT = "{}://{}/predict/api/retail/{}/ack_server_impressions"

# The URL format of data uploading
# Example: https://tob.sgsnssdk.com/data/api/retail/retail_demo/user?method=write
_UPLOAD_URL_FORMAT = "{}://{}/data/api/retail/{}/{}?method={}"


class _RetailURL(CommonURL):

    def __init__(self, context: Context):
        super().__init__(context)
        # The URL template of "predict" request, which need fill with "scene" info when use
        # Example: https://tob.sgsnssdk.com/predict/api/retail/demo/home
        self.predict_url_format: str = ""
        # The URL of reporting the real exposure list
        # Example: https://tob.sgsnssdk.com/predict/api/retail/demo/ack_server_impression
        self.ack_impression_url: str = ""
        # The URL of uploading real-time user data
        # Example: https://tob.sgsnssdk.com/data/api/retail/retail_demo/user?method=write
        self.write_users_url: str = ""
        # The URL of importing daily offline user data
        # Example: https://tob.sgsnssdk.com/data/api/retail/retail_demo/user?method=import
        self.import_users_url: str = ""
        # The URL of uploading real-time product data
        # Example: https://tob.sgsnssdk.com/data/api/retail/retail_demo/product?method=write
        self.write_products_url: str = ""
        # The URL of importing daily offline product data
        # Example: https://tob.sgsnssdk.com/data/api/retail/retail_demo/product?method=import
        self.import_products_url: str = ""
        # The URL of uploading real-time user event data
        # Example: https://tob.sgsnssdk.com/data/api/retail/retail_demo/user_event?method=write
        self.write_user_events_url: str = ""
        # The URL of importing daily offline product data
        # Example: https://tob.sgsnssdk.com/data/api/retail/retail_demo/user_event?method=import
        self.import_user_events_url: str = ""
        self.refresh(context.hosts[0])

    def refresh(self, host: str) -> None:
        super().refresh(host)
        self.predict_url_format: str = self._generate_predict_url(host)
        self.ack_impression_url: str = self._generate_ack_url(host)
        self.write_users_url: str = self._generate_upload_url(host, "user", "write")
        self.import_users_url: str = self._generate_upload_url(host, "user", "import")
        self.write_products_url: str = self._generate_upload_url(host, "product", "write")
        self.import_products_url: str = self._generate_upload_url(host, "product", "import")
        self.write_user_events_url: str = self._generate_upload_url(host, "user_event", "write")
        self.import_user_events_url: str = self._generate_upload_url(host, "user_event", "import")

    def _generate_predict_url(self, host) -> str:
        return _PREDICT_URL_FORMAT.format(self.schema, host, self.tenant)

    def _generate_ack_url(self, host) -> str:
        return _ACK_IMPRESSION_URL_FORMAT.format(self.schema, host, self.tenant)

    def _generate_upload_url(self, host, topic, method) -> str:
        return _UPLOAD_URL_FORMAT.format(self.schema, host, self.tenant, topic, method)