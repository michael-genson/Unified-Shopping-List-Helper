import json
from typing import Any, Optional, Union, cast

from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_request_type
from ask_sdk_model import Response
from ask_sdk_model.interfaces.messaging.message_received_request import (
    MessageReceivedRequest,
)
from ask_sdk_model.services.list_management.error import Error
from ask_sdk_model.services.service_exception import ServiceException

from ..config import CALLBACK_EVENT_EXPIRATION, CALLBACK_EVENT_TABLENAME
from ..interfaces.dynamodb import DynamoDB
from ..interfaces.list_management import ListManagement
from ..models.dynamodb import CallbackEvent
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
from ..models.messages import (
    Message,
    MessageResponse,
    MessageResponseBody,
    ObjectType,
    Operation,
)
from ..skill import sb

event_db = DynamoDB(CALLBACK_EVENT_TABLENAME)


@sb.request_handler(can_handle_func=is_request_type("Messaging.MessageReceived"))
def route_message(input: HandlerInput) -> Response:
    client = input.service_client_factory.get_list_management_service()
    list_management = ListManagement(client)

    request = cast(
        MessageReceivedRequest,
        input.request_envelope.request,
    )

    message_data = request.message
    if not message_data:
        return input.response_builder.response

    msg = Message.parse_obj(message_data)
    print("message received:", msg)

    # default response if there is no operation + object_type match
    response_body: MessageResponseBody = MessageResponseBody(
        success=False, detail="invalid operation + object_type parameters"
    )

    try:
        responses: list[dict[str, Any]] = []
        for msg_request in msg.requests:
            response: Optional[Union[Error, object]] = None
            response_data: Optional[dict[str, Any]] = None

            if msg_request.operation == Operation.read_all:
                if msg_request.object_type == ObjectType.list:
                    response = list_management.read_all_lists()
                    response_data = response.to_dict()

            elif msg_request.operation == Operation.read:
                if msg_request.object_type == ObjectType.list:
                    response = list_management.read_list(
                        ReadList.parse_obj(msg_request.object_data)
                    )
                    response_data = response.to_dict()

                elif msg_request.object_type == ObjectType.list_item:
                    response = list_management.read_list_item(
                        ReadListItem.parse_obj(msg_request.object_data)
                    )
                    response_data = response.to_dict()

            else:
                if msg_request.object_type == ObjectType.list:
                    if msg_request.operation == Operation.create:
                        response = list_management.create_list(
                            CreateList.parse_obj(msg_request.object_data)
                        )
                        response_data = response.to_dict()

                    elif msg_request.operation == Operation.update:
                        response = list_management.update_list(
                            UpdateList.parse_obj(msg_request.object_data)
                        )

                        if response:
                            response_data = response.to_dict()

                    elif msg_request.operation == Operation.delete:
                        response = list_management.delete_list(
                            DeleteList.parse_obj(msg_request.object_data)
                        )

                        if response:
                            response_data = response.to_dict()

                elif msg_request.object_type == ObjectType.list_item:
                    if msg_request.operation == Operation.create:
                        response = list_management.create_list_item(
                            CreateListItem.parse_obj(msg_request.object_data)
                        )

                        response_data = response.to_dict()

                    elif msg_request.operation == Operation.update:
                        response = list_management.update_list_item(
                            UpdateListItem.parse_obj(msg_request.object_data)
                        )

                        if response:
                            response_data = response.to_dict()

                    elif msg_request.operation == Operation.delete:
                        response = list_management.delete_list_item(
                            DeleteListItem.parse_obj(msg_request.object_data)
                        )

                        if response:
                            response_data = response.to_dict()

            if response_data:
                response_data["metadata"] = msg_request.metadata
                responses.append(response_data)

    except ServiceException:
        response_body = MessageResponseBody(
            success=False,
            detail="Alexa service exception; are the provided object ids accurate?",
        )

    else:
        response_body = MessageResponseBody(
            success=not isinstance(response, Error),
            data=responses,
        )

    message_response = MessageResponse(source_message=msg, body=response_body)

    # write response to DynamoDB
    if msg.send_callback_response:
        callback = CallbackEvent(
            event_source=message_response.source_message.source,
            event_id=message_response.source_message.event_id,
            data=json.dumps(message_response.body.dict(exclude_none=True)),
        )

        event_db.put(callback.dict(exclude_none=True), CALLBACK_EVENT_EXPIRATION)

    print("response:", message_response)
    input.response_builder.set_api_response(message_response.dict(exclude_none=True))
    return input.response_builder.response
