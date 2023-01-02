from typing import Optional, Union, cast

from ask_sdk_model.services.list_management.alexa_list import AlexaList
from ask_sdk_model.services.list_management.alexa_list_item import AlexaListItem
from ask_sdk_model.services.list_management.alexa_list_metadata import AlexaListMetadata
from ask_sdk_model.services.list_management.alexa_lists_metadata import (
    AlexaListsMetadata,
)
from ask_sdk_model.services.list_management.error import Error
from ask_sdk_model.services.list_management.list_management_service_client import (
    ListManagementServiceClient,
)

from ..models.lists import (
    CreateList,
    CreateListItem,
    DeleteList,
    DeleteListItem,
    ReadList,
    ReadListItem,
    UpdateList,
    UpdateListItem,
)


class ListManagement:
    """Wrapper for the Alexa List Management Service Client"""

    def __init__(self, client: ListManagementServiceClient) -> None:
        self.client = client

    def read_all_lists(
        self,
    ) -> Union[AlexaListsMetadata, Error]:
        response = self.client.get_lists_metadata()
        if isinstance(response, Error):
            return response

        return cast(AlexaListsMetadata, response)

    def read_list(self, alexa_list: ReadList) -> Union[AlexaList, Error]:
        response = self.client.get_list(list_id=alexa_list.list_id, status=alexa_list.state.value)
        if isinstance(response, Error):
            return response

        return cast(AlexaList, response)

    def create_list(self, alexa_list: CreateList) -> Union[AlexaListMetadata, Error]:
        response = self.client.create_list(alexa_list.request())
        if isinstance(response, Error):
            return response

        return cast(AlexaListMetadata, response)

    def update_list(self, alexa_list: UpdateList) -> Optional[Error]:
        response = self.client.update_list(alexa_list.list_id, alexa_list.request())
        if isinstance(response, Error):
            return response

        return None

    def delete_list(self, alexa_list: DeleteList) -> Optional[Error]:
        response = self.client.delete_list(alexa_list.list_id)
        if isinstance(response, Error):
            return response

        return None

    def read_list_item(self, list_item: ReadListItem) -> Union[AlexaListItem, Error]:
        response = self.client.get_list_item(list_id=list_item.list_id, item_id=list_item.item_id)
        if isinstance(response, Error):
            return response

        return cast(AlexaListItem, response)

    def create_list_item(self, alexa_item: CreateListItem) -> Union[AlexaListItem, Error]:
        response = self.client.create_list_item(alexa_item.list_id, alexa_item.request())
        if isinstance(response, Error):
            return response

        return cast(AlexaListItem, response)

    def update_list_item(self, alexa_item: UpdateListItem) -> Optional[Error]:
        response = self.client.update_list_item(
            alexa_item.list_id, alexa_item.item_id, alexa_item.request()
        )
        if isinstance(response, Error):
            return response

        return None

    def delete_list_item(self, alexa_item: DeleteListItem) -> Optional[Error]:
        response = self.client.delete_list_item(alexa_item.list_id, alexa_item.item_id)
        if isinstance(response, Error):
            return response

        return None
