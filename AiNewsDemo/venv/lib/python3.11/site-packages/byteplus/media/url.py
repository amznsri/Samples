from byteplus.common.url import CommonURL
from byteplus.core.context import Context

# The URL format of data uploading
# Example: https://tob.sgsnssdk.com/data/api/media/media_demo/user?method=write
_UPLOAD_URL_FORMAT = "{}://{}/data/api/media/{}/{}?method={}"

# The URL template of "predict" request, which need fill with "scene" info when use
# Example: https://tob.sgsnssdk.com/predict/api/media/media_demo/home
_PREDICT_URL_FORMAT = "{}://{}/predict/api/media/{}/#"

# The URL format of reporting the real exposure list
# Example: https://tob.sgsnssdk.com/predict/api/media/media_demo/ack_impression
_ACK_IMPRESSION_URL_FORMAT = "{}://{}/predict/api/media/{}/ack_server_impressions"


class _MediaURL(CommonURL):
    def __init__(self, context: Context):
        super().__init__(context)
        # The URL of uploading real-time user data
        # Example: https://tob.sgsnssdk.com/data/api/media/media_demo/user?method=write
        self.write_users_url: str = ""
        # The URL of uploading real-time content data
        # Example: https://tob.sgsnssdk.com/data/api/media/media_demo/content?method=write
        self.write_contents_url: str = ""
        # The URL of uploading real-time user event data
        # Example: https://tob.sgsnssdk.com/data/api/media/media_demo/user_event?method=write
        self.write_user_events_url: str = ""
        # The URL template of "predict" request, which need fill with "scene" info when use
        # Example: https://tob.sgsnssdk.com/predict/api/media/media_demo/home
        self.predict_url_format: str = ""
        # The URL of reporting the real exposure list
        # Example: https://tob.sgsnssdk.com/predict/api/media/media_demo/ack_server_impression
        self.ack_impression_url: str = ""
        self.refresh(context.hosts[0])

    def refresh(self, host: str) -> None:
        super().refresh(host)
        self.write_users_url: str = self._generate_upload_url(host, "user", "write")
        self.write_contents_url: str = self._generate_upload_url(host, "content", "write")
        self.write_user_events_url: str = self._generate_upload_url(host, "user_event", "write")
        self.predict_url_format: str = self._generate_predict_url(host)
        self.ack_impression_url: str = self._generate_ack_url(host)

    def _generate_upload_url(self, host, topic, method) -> str:
        return _UPLOAD_URL_FORMAT.format(self.schema, host, self.tenant, topic, method)

    def _generate_predict_url(self, host) -> str:
        return _PREDICT_URL_FORMAT.format(self.schema, host, self.tenant)

    def _generate_ack_url(self, host) -> str:
        return _ACK_IMPRESSION_URL_FORMAT.format(self.schema, host, self.tenant)
