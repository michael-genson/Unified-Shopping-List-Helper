import logging
import time
from datetime import datetime
from typing import Union, cast

from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_request_type
from ask_sdk_core.utils.request_util import get_account_linking_access_token
from ask_sdk_model import Response
from ask_sdk_model.services.list_management.error import Error
from ask_sdk_model.services.list_management.list_item_state import ListItemState
from ask_sdk_model.services.list_management.list_items_created_event_request import (
    ListItemsCreatedEventRequest,
)
from ask_sdk_model.services.list_management.list_items_deleted_event_request import (
    ListItemsDeletedEventRequest,
)
from ask_sdk_model.services.list_management.list_items_updated_event_request import (
    ListItemsUpdatedEventRequest,
)

from ..interfaces.list_management import ListManagement
from ..interfaces.shopping_list_api import ShoppingListAPIInterface
from ..models.lists import ReadList
from ..models.messages import Message, MessageRequest, ObjectType, Operation
from ..models.shopping_list_api import ShoppingListAPIListEvent
from ..skill import USL_BASE_URL, sb

# TODO: handle archived and deleted lists (unlink list maps in USL)


def is_list_item_event(input: HandlerInput) -> bool:
    return any(
        [
            is_request_type("AlexaHouseholdListEvent.ItemsCreated")(input),
            is_request_type("AlexaHouseholdListEvent.ItemsUpdated")(input),
            is_request_type("AlexaHouseholdListEvent.ItemsDeleted")(input),
        ]
    )


@sb.request_handler(can_handle_func=is_list_item_event)
def handle_list_item_event(input: HandlerInput) -> Response:
    list_management_client = input.service_client_factory.get_list_management_service()
    list_management = ListManagement(list_management_client)

    operation: Operation
    request: Union[ListItemsCreatedEventRequest, ListItemsUpdatedEventRequest, ListItemsDeletedEventRequest]
    if is_request_type("AlexaHouseholdListEvent.ItemsCreated")(input):
        operation = Operation.create
        request = cast(ListItemsCreatedEventRequest, input.request_envelope.request)

    elif is_request_type("AlexaHouseholdListEvent.ItemsUpdated")(input):
        operation = Operation.update
        request = cast(ListItemsUpdatedEventRequest, input.request_envelope.request)

    elif is_request_type("AlexaHouseholdListEvent.ItemsDeleted")(input):
        operation = Operation.delete
        request = cast(ListItemsDeletedEventRequest, input.request_envelope.request)

    else:
        raise Exception("unsupported event; is the request handler configured correctly?")

    logging.info(f"received list item {operation.value} event {request.request_id}")

    request = cast(ListItemsCreatedEventRequest, input.request_envelope.request)
    access_token = get_account_linking_access_token(input)

    if not request.body or not request.body.list_item_ids:
        raise ValueError("Request body and list item ids should not be null")

    if not access_token:
        logging.info("User is not linked to USL; aborting")
        return input.response_builder.response

    # send the items to the shopping list API
    list_event = ShoppingListAPIListEvent(
        request_id=request.request_id,
        timestamp=request.timestamp or datetime.now(),
        operation=operation,
        object_type=ObjectType.list_item,
        list_id=request.body.list_id,
        list_item_ids=request.body.list_item_ids,
    )

    shopping_list_api_client = ShoppingListAPIInterface(USL_BASE_URL, str(access_token))
    shopping_list_api_client.post_list_item_event(list_event)

    response = Message(
        source="Alexa",
        event_id=request.request_id,
        requests=[
            MessageRequest(
                operation=operation,
                object_type=ObjectType.list_item,
            )
        ],
    )

    return handle_event_response(input, response)


def handle_event_response(input: HandlerInput, response: Message) -> Response:
    input.response_builder.set_api_response(response.dict(exclude_none=True))
    return input.response_builder.response
