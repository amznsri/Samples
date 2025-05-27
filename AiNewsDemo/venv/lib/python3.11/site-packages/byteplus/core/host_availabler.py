import logging
import threading
import time
import uuid

import requests
from requests import Response

from byteplus.core.context import Context
from byteplus.core.host_availabler_config import Config
from byteplus.core.metrics.metrics_log import MetricsLog
from byteplus.core.url_center import URLCenter

log = logging.getLogger(__name__)

_FAILURE_RATE_THRESHOLD: float = 0.1
_PING_SUCCESS_HTTP_CODE = 200


class HostAvailabler(object):
    def __init__(self, url_center: URLCenter, context: Context):
        config: Config = context.host_availabler_config
        if config is None:
            config = Config()
        self._config: Config = config
        self._url_center: URLCenter = url_center
        self._context: Context = context
        self._ping_url_format = self._config.ping_url_format.replace("#", context.schema)
        self._available_hosts: list = context.hosts
        self._current_host: str = context.hosts[0]
        self._host_window_map: dict = {}
        self._abort: bool = False
        if len(context.hosts) <= 1:
            return
        for host in context.hosts:
            self._host_window_map[host] = _Window(self._config.window_size)
        threading.Thread(target=self._start_schedule).start()
        return

    def get_host(self) -> str:
        return self._current_host

    def shutdown(self):
        self._abort = True

    def _start_schedule(self) -> None:
        if self._abort:
            return
        # log.debug("[ByteplusSDK] http")
        self._check_host()
        # a timer only execute once after spec duration
        timer = threading.Timer(self._config.ping_interval_seconds, self._start_schedule)
        timer.start()
        return

    def _check_host(self) -> None:
        self._do_check_host()
        self._switch_host()

    def _do_check_host(self) -> None:
        self._available_hosts = []
        for host in self._context.hosts:
            window = self._host_window_map[host]
            success = self._ping(host)
            window.put(success)
            if window.failure_rate() < _FAILURE_RATE_THRESHOLD:
                self._available_hosts.append(host)
        if len(self._available_hosts) <= 1:
            return
        self._available_hosts.sort(key=lambda item: self._host_window_map[item].failure_rate())

    def _ping(self, host) -> bool:
        url: str = self._ping_url_format.format(host)
        headers = self._context.customer_headers
        req_id: str = "ping_" + str(uuid.uuid1())
        headers = headers.update({
            "Request-Id": req_id,
            "Tenant": self._context.tenant,
        })
        start = time.time()
        try:
            rsp: Response = requests.get(url, headers=headers, timeout=self._config.ping_timeout_seconds)
            cost = int((time.time() - start) * 1000)
            if rsp.status_code != _PING_SUCCESS_HTTP_CODE:
                MetricsLog.warn(req_id, "[ByteplusSDK] ping fail, tenant:{}, host:{}, cost:{}ms, status:{}",
                                self._context.tenant, host, cost, rsp.status_code)
            else:
                MetricsLog.info(req_id, "[ByteplusSDK] ping success, tenant:{}, host:{}, cost:{}ms",
                                self._context.tenant, host, cost)
        except BaseException as e:
            cost = int((time.time() - start) * 1000)
            MetricsLog.warn(req_id, "[ByteplusSDK] ping find err, tenant:{}, host:{}, cost:{}ms, err:{}",
                            self._context.tenant, host, cost, e)
            log.warning("[ByteplusSDK] ping find err, host:'%s' err:'%s'", host, e)
            return False
        finally:
            cost = int((time.time() - start) * 1000)
            log.debug("[ByteplusSDK] http path:%s, cost:%dms", url, cost)
        return rsp.status_code == _PING_SUCCESS_HTTP_CODE

    def _switch_host(self) -> None:
        if len(self._available_hosts) == 0:
            new_host = self._context.hosts[0]
        else:
            new_host = self._available_hosts[0]
        if new_host != self._current_host:
            log.warning("[ByteplusSDK] switch host to '%s', origin:'%s'",
                        new_host, self._current_host)
            self._current_host = new_host
            self._url_center.refresh(new_host)


class _Window(object):
    def __init__(self, size: int):
        self.size: int = size
        self.head: int = size - 1
        self.tail: int = 0
        self.items: list = [True] * size
        self.failure_count: int = 0

    def put(self, success: bool) -> None:
        if not success:
            self.failure_count += 1
        self.head = (self.head + 1) % self.size
        self.items[self.head] = success
        self.tail = (self.tail + 1) % self.size
        removing_item = self.items[self.tail]
        if not removing_item:
            self.failure_count -= 1

    def failure_rate(self) -> float:
        return self.failure_count / self.size
