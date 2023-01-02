import time
from typing import Optional

import requests
from requests import HTTPError, Response

STATUS_CODES_TO_RETRY = [429, 500]


class ShoppingListAPIClient:
    """Low-level client for interacting with the Shopping List API"""

    def __init__(
        self,
        base_url: str,
        auth_token: str,
        timeout: int = 30,
        rate_limit_throttle: int = 5,
        max_attempts: int = 3,
    ) -> None:
        if not base_url:
            raise ValueError("base_url must not be empty")

        if base_url[-1] != "/":
            base_url += "/"

        if "http" not in base_url:
            base_url = "https://" + base_url

        self.base_url = base_url
        self._client = requests.session()
        self._client.headers.update(
            {
                "content-type": "application/json",
                "Authorization": f"Bearer {auth_token}",
            }
        )

        self.timeout = timeout
        self.rate_limit_throttle = rate_limit_throttle
        self.max_attempts = max_attempts

    def _request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        payload: Optional[dict] = None,
    ) -> Response:
        if not endpoint or endpoint == "/":
            raise ValueError("endpoint must not be empty")

        if endpoint[0] == "/":
            endpoint = endpoint[1:]

        url = self.base_url + endpoint

        attempt = 0
        while True:
            attempt += 1
            try:
                r = self._client.request(
                    method.upper(),
                    url,
                    headers=headers,
                    params=params,
                    json=payload,
                    timeout=self.timeout,
                )
                r.raise_for_status()
                return r

            except HTTPError as e:
                if attempt >= self.max_attempts:
                    raise

                response: Response = e.response
                if response.status_code not in STATUS_CODES_TO_RETRY:
                    raise

                time.sleep(self.rate_limit_throttle)
                continue

    def get(
        self, endpoint: str, headers: Optional[dict] = None, params: Optional[dict] = None
    ) -> Response:
        return self._request("GET", endpoint, headers, params)

    def head(
        self, endpoint: str, headers: Optional[dict] = None, params: Optional[dict] = None
    ) -> Response:
        return self._request("HEAD", endpoint, headers, params)

    def patch(
        self,
        endpoint: str,
        payload: Optional[dict] = None,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Response:
        return self._request("PATCH", endpoint, headers, params, payload)

    def post(
        self,
        endpoint: str,
        payload: Optional[dict] = None,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Response:
        return self._request("POST", endpoint, headers, params, payload)

    def put(
        self,
        endpoint: str,
        payload: Optional[dict] = None,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Response:
        return self._request("PUT", endpoint, headers, params, payload)

    def delete(
        self,
        endpoint: str,
        payload: Optional[dict] = None,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Response:
        return self._request("DELETE", endpoint, headers, params, payload)
