MAX_WRITE_ITEM_COUNT: int = 2000

MAX_IMPORT_ITEM_COUNT: int = 10000

_CN_HOSTS: list = ["rec.volcengineapi.com", "rec-b.volcengineapi.com"]

_SG_HOSTS: list = ["rec-ap-singapore-1.byteplusapi.com", "rec-b-ap-singapore-1.byteplusapi.com"]

_US_HOSTS: list = ["rec-us-east-1.byteplusapi.com", "rec-b-us-east-1.byteplusapi.com"]

# All requests will have a XXXResponse corresponding to them,
# and a‘ll XXXResponses will contain a 'Status' field.
# The status of this request can be determined by the value of `Status.Code`
# Detail error code info：https://docs.byteplus.com/docs/error-code

# The request was executed successfully without any exception
STATUS_CODE_SUCCESS: int = 0
# A Request with the same "Request-ID" was already received. This Request was rejected
STATUS_CODE_IDEMPOTENT: int = 409
# Operation information is missing due to an unknown exception
STATUS_CODE_OPERATION_LOSS: int = 410
# The server hope slow down request frequency, and this request was rejected
STATUS_CODE_TOO_MANY_REQUEST: int = 429

VOLC_AUTH_SERVICE = "air"

# Metrics Key
METRICS_KEY_COMMON_ERROR = "common.err"
METRICS_KEY_REQUEST_TOTAL_COST = "request.total.cost"
METRICS_KEY_REQUEST_COUNT = "request.count"
