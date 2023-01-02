import time
from typing import cast

from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_request_type
from ask_sdk_core.utils.request_util import get_account_linking_access_token
from ask_sdk_model import Response
from ask_sdk_model.services.list_management.error import Error
from ask_sdk_model.services.list_management.list_item_state import ListItemState
from ask_sdk_model.services.list_management.list_items_created_event_request import (
    ListItemsCreatedEventRequest,
)

from ..interfaces.list_management import ListManagement
from ..interfaces.shopping_list_api import ShoppingListAPIInterface
from ..models.lists import ReadList, UpdateListItem
from ..models.messages import Message, ObjectType, Operation
from ..models.shopping_list_api import ShoppingListAPIListItem, ShoppingListAPIListItems
from ..skill import USL_BASE_URL, sb

# TODO: handle archived and deleted lists


@sb.request_handler(can_handle_func=is_request_type("AlexaHouseholdListEvent.ItemsCreated"))
def list_items_created(input: HandlerInput) -> Response:
    list_management_client = input.service_client_factory.get_list_management_service()
    list_management = ListManagement(list_management_client)

    request = cast(ListItemsCreatedEventRequest, input.request_envelope.request)
    print(f"received list items created event {request.request_id}")

    if not request.body or not request.body.list_item_ids:
        raise ValueError("Request body and list item ids should not be null")

    # fetch the list and all its items
    time.sleep(1)  # give Alexa some time to process multiple events in quick-succession
    read_list = ReadList(list_id=request.body.list_id)
    alexa_list = list_management.read_list(read_list)

    if isinstance(alexa_list, Error):
        print("There was an error when trying to read the Alexa list", alexa_list)
        return input.response_builder.response

    # if we don't have any of the created items, we end early
    if not alexa_list.items:
        print("no new items found")
        return input.response_builder.response

    # only handle active items that actually got created
    alexa_list.items = [
        item
        for item in alexa_list.items
        if item.id
        and item.id in request.body.list_item_ids
        and item.status == ListItemState.active
    ]

    # if we filtered out all items, end early
    if not alexa_list.items:
        print("no new items found")
        return input.response_builder.response

    # send the items to the shopping list API
    if shopping_list_api_auth_token := get_account_linking_access_token(input):
        shopping_list_api_client = ShoppingListAPIInterface(
            USL_BASE_URL, str(shopping_list_api_auth_token)
        )

        list_items = [
            ShoppingListAPIListItem(
                list_id=alexa_list.list_id,
                item_id=item.id,
                value=item.value,
                status=item.status,
            )
            for item in alexa_list.items
        ]

        list_item_collection = ShoppingListAPIListItems(list_items=list_items)
        created_item_collection = shopping_list_api_client.create_shopping_list_items(
            list_item_collection
        )

        created_item_ids = [item.item_id for item in created_item_collection.list_items]

        # check off the items that were created
        for item in alexa_list.items:
            if item.id not in created_item_ids:
                continue

            try:
                checked_item = UpdateListItem(
                    list_id=alexa_list.list_id,
                    item_id=item.id,
                    value=item.value,
                    status=ListItemState.completed,
                    version=item.version,
                )

                list_management.update_list_item(checked_item)

            except Exception as e:
                continue

    response = Message(
        source="Alexa",
        event_id=request.request_id,
        operation=Operation.create,
        object_type=ObjectType.list_item,
        object_data=alexa_list.to_dict(),
    )

    return handle_event_response(input, response)


def handle_event_response(input: HandlerInput, response: Message) -> Response:
    input.response_builder.set_api_response(response.dict(exclude_none=True))
    return input.response_builder.response
