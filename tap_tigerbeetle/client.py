"""HTTP API client (REST or GraphQL), including TigerbeetleStream base class."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

import requests
from hotglue_singer_sdk.streams import RESTStream
from typing_extensions import override
import tigerbeetle as tb
import copy
import os

class TigerbeetleStream(RESTStream):
    """Tigerbeetle stream class."""

    records_jsonpath = "$[*]"
    url_base = ""


    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Any | None,
    ) -> Any | None:
        next_page_token = len(response)
        if next_page_token == 50:
            return response[-1].timestamp
        return None

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        for record in response:
            yield asdict(record)

    @override
    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token is not None:
            params["timestamp_min"] = next_page_token
        return params

    def request_records(self, context: dict | None) -> Iterable[dict]:
        """Request records from REST endpoint(s), returning response records.

        If pagination is detected, pages will be recursed automatically.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            An item for every record in the response.

        Raises:
            RuntimeError: If a loop in pagination is detected. That is, when two
                consecutive pagination tokens are identical.
        """
        next_page_token: Any | None = None
        finished = False
        decorated_request = self.request_decorator(self._request)

        # init TB client
        with tb.ClientSync(cluster_id=0, replica_addresses=os.getenv("TB_ADDRESS", "3000")) as client:
            while not finished:
                prepared_request = self.prepare_request(
                    context, next_page_token=next_page_token
                )
                resp = decorated_request(prepared_request, context, client=client)
                yield from self.parse_response(resp)
                previous_token = copy.deepcopy(next_page_token)
                next_page_token = self.get_next_page_token(
                    response=resp, previous_token=previous_token
                )
                if next_page_token and next_page_token == previous_token:
                    raise RuntimeError(
                        f"Loop detected in pagination. "
                        f"Pagination token {next_page_token} is identical to prior token."
                    )
                # Cycle until get_next_page_token() no longer returns a value
                finished = not next_page_token