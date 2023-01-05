from datetime import datetime
from typing import Optional

from ask_sdk_model.services.list_management.list_item_state import ListItemState

from ._base import AlexaBase
from .messages import ObjectType, Operation


class ShoppingListAPIListItem(AlexaBase):
    id: str
    value: str
    status: ListItemState = ListItemState.active

    class Config:
        use_enum_values = True


class ShoppingListAPIListItems(AlexaBase):
    list_id: str
    list_items: list[ShoppingListAPIListItem]


class ShoppingListAPIListEvent(AlexaBase):
    request_id: str
    timestamp: datetime

    operation: Operation
    object_type: ObjectType

    list_id: str
    list_item_ids: Optional[list[str]] = []
    """only populated in list item events"""

    class Config:
        use_enum_values = True
