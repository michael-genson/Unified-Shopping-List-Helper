from requests import HTTPError

from ..clients.shopping_list_api import ShoppingListAPIClient
from ..config import (
    SHOPPING_LIST_API_CREATE_LIST_ITEMS_ROUTE,
    SHOPPING_LIST_API_VALIDATION_ROUTE,
)
from ..models.shopping_list_api import ShoppingListAPIListItems


class ShoppingListAPIInterface:
    def __init__(self, base_url: str, auth_token: str) -> None:
        self._client = ShoppingListAPIClient(base_url, auth_token)

    @property
    def is_valid(self) -> bool:
        """Call the Shopping List API and check if the configuration is valid"""

        try:
            self._client.get(SHOPPING_LIST_API_VALIDATION_ROUTE)
            return True

        except HTTPError:
            return False

    def create_shopping_list_items(
        self, items: ShoppingListAPIListItems
    ) -> ShoppingListAPIListItems:
        response = self._client.post(
            SHOPPING_LIST_API_CREATE_LIST_ITEMS_ROUTE, payload=items.dict()
        )

        return ShoppingListAPIListItems.parse_obj(response.json())
