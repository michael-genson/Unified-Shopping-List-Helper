from typing import Optional

from ask_sdk_model.services.list_management.create_list_item_request import (
    CreateListItemRequest,
)
from ask_sdk_model.services.list_management.create_list_request import CreateListRequest
from ask_sdk_model.services.list_management.list_item_state import ListItemState
from ask_sdk_model.services.list_management.list_state import ListState
from ask_sdk_model.services.list_management.update_list_item_request import (
    UpdateListItemRequest,
)
from ask_sdk_model.services.list_management.update_list_request import UpdateListRequest

from ..models._base import AlexaBase


### List###
class ReadList(AlexaBase):
    list_id: str
    state: ListState = ListState.active


class CreateList(AlexaBase):
    name: str
    state: ListState = ListState.active

    def request(self) -> CreateListRequest:
        return CreateListRequest(self.name, self.state)


class UpdateList(AlexaBase):
    list_id: str
    name: str
    state: ListState = ListState.active
    version: int

    def request(self) -> UpdateListRequest:
        return UpdateListRequest(name=self.name, state=self.state, version=self.version)


class DeleteList(AlexaBase):
    list_id: str


### List Item ###
class ReadListItem(AlexaBase):
    list_id: str
    item_id: str


class CreateListItem(AlexaBase):
    list_id: str
    value: str
    status: ListItemState = ListItemState.active

    def request(self) -> CreateListItemRequest:
        return CreateListItemRequest(value=self.value, status=self.status)


class UpdateListItem(AlexaBase):
    list_id: str
    item_id: str
    value: str
    status: ListItemState = ListItemState.active
    version: int

    def request(self) -> UpdateListItemRequest:
        return UpdateListItemRequest(value=self.value, status=self.status, version=self.version)


class DeleteListItem(AlexaBase):
    list_id: str
    item_id: str
