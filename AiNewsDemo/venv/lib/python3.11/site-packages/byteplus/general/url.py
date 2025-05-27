from byteplus.common.url import CommonURL
from byteplus.core.context import Context

# The URL template of "predict" request, which need fill with "scene" info when use
# Example: https://tob.sgsnssdk.com/predict/api/general_demo/home
_PREDICT_URL_FORMAT = "{}://{}/predict/api/{}/#"

# The URL format of reporting the real exposure list
# Example: https://tob.sgsnssdk.com/predict/api/general_demo/callback
_CALLBACK_URL_FORMAT = "{}://{}/predict/api/{}/callback"

# The URL format of data uploading
# Example: https://tob.sgsnssdk.com/data/api/general_demo/user?method=write
_UPLOAD_URL_FORMAT = "{}://{}/data/api/{}/#?method={}"

# The URL format of marking a whole day data has been imported completely
# Example: https://tob.sgsnssdk.com/predict/api/general_demo/done?topic=user
_DONE_URL_FORMAT = "{}://{}/data/api/{}/done?topic=#"


class _GeneralURL(CommonURL):

    def __init__(self, context: Context):
        super().__init__(context)
        # The URL template of "predict" request, which need fill with "scene" info when use
        # Example: https://tob.sgsnssdk.com/predict/api/general_demo/home
        self.predict_url_format: str = ""

        # The URL of reporting the real exposure list
        # Example: https://tob.sgsnssdk.com/predict/api/general_demo/callback
        self.callback_url: str = ""

        # The URL of uploading real-time user data
        # Example: https://tob.sgsnssdk.com/data/api/general_demo/user?method=write
        self.write_data_url_format: str = ""

        # The URL of importing daily offline user data
        # Example: https://tob.sgsnssdk.com/data/api/general_demo/user?method=import
        self.import_data_url_format: str = ""

        # The URL format of marking a whole day data has been imported completely
        # Example: https://tob.sgsnssdk.com/predict/api/general_demo/done?topic=user
        self.done_url_format: str = ""
        self.refresh(context.hosts[0])

    def refresh(self, host: str) -> None:
        super().refresh(host)
        self.predict_url_format: str = self._generate_predict_url(host)
        self.callback_url: str = self._generate_callback_url(host)
        self.write_data_url_format: str = self._generate_upload_url(host, "write")
        self.import_data_url_format: str = self._generate_upload_url(host, "import")
        self.done_url_format: str = self._generate_done_url(host)

    def _generate_predict_url(self, host) -> str:
        return _PREDICT_URL_FORMAT.format(self.schema, host, self.tenant)

    def _generate_callback_url(self, host) -> str:
        return _CALLBACK_URL_FORMAT.format(self.schema, host, self.tenant)

    def _generate_upload_url(self, host, method) -> str:
        return _UPLOAD_URL_FORMAT.format(self.schema, host, self.tenant, method)

    def _generate_done_url(self, host) -> str:
        return _DONE_URL_FORMAT.format(self.schema, host, self.tenant)
