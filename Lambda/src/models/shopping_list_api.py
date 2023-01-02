from ask_sdk_model.services.list_management.list_item_state import ListItemState

from ._base import AlexaBase


class ShoppingListAPIListItem(AlexaBase):
    id: str
    value: str
    status: ListItemState = ListItemState.active

    class Config:
        use_enum_values = True


class ShoppingListAPIListItems(AlexaBase):
    list_id: str
    list_items: list[ShoppingListAPIListItem]
