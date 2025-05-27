import time
from datetime import timedelta, datetime, timezone, tzinfo
from typing import List


def rfc3339_format(dt: datetime) -> str:
    return dt.astimezone().isoformat()


def milliseconds(delta: timedelta) -> int:
    return int(delta.total_seconds() * 1000.0)


def current_time_millis() -> int:
    return int(time.time() * 1000)


def none_empty_str(st: List[str]) -> bool:
    if str is None:
        return False
    for s in st:
        if s is None or len(s) == 0:
            return False
    return True


def is_all_empty_str(st: List[str]) -> bool:
    if st is None:
        return True
    for s in st:
        if s is not None and len(s) > 0:
            return False
    return True


def is_empty_str(st: str) -> bool:
    return st is None or len(st) == 0


def escape_metrics_tag_value(value: str) -> str:
    value = value.replace("?", "-qu-", -1)
    value = value.replace("&", "-and-", -1)
    value = value.replace("=", "-eq-", -1)
    return value


def is_timeout_exception(e):
    lower_err_msg = str(e).lower()
    if "time" in lower_err_msg and "out" in lower_err_msg:
        return True
    return False
