from requests import HTTPError

from ..clients.shopping_list_api import ShoppingListAPIClient
from ..config import (
    SHOPPING_LIST_API_POST_ITEM_EVENTS_ROUTE,
    SHOPPING_LIST_API_VALIDATION_ROUTE,
)
from ..models.shopping_list_api import ShoppingListAPIListEvent


class ShoppingListAPIInterface:
    def __init__(self, base_url: str, auth_token: str) -> None:
        self._client = ShoppingListAPIClient(base_url, auth_token)

    @property
    def is_valid(self) -> bool:
        """Call the Unified Shopping List API and check if the configuration is valid"""

        try:
            self._client.get(SHOPPING_LIST_API_VALIDATION_ROUTE)
            return True

        except HTTPError:
            return False

    def post_list_item_event(self, list_event: ShoppingListAPIListEvent) -> None:
        """Post a list item event to the Unified Shopping List API"""

        list_event_payload = list_event.dict()
        list_event_payload["timestamp"] = list_event_payload["timestamp"].isoformat()

        self._client.post(SHOPPING_LIST_API_POST_ITEM_EVENTS_ROUTE, payload=list_event_payload)
