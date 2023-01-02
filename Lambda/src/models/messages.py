from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


class Operation(Enum):
    create = "create"
    read = "read"
    read_all = "read_all"
    update = "update"
    delete = "delete"


class ObjectType(Enum):
    list = "list"
    list_item = "list_item"


class MessageRequest(BaseModel):
    operation: Operation
    object_type: ObjectType
    object_data: Optional[dict[str, Any]]

    metadata: Optional[dict[str, Any]]


class Message(BaseModel):
    source: str
    event_id: str
    requests: list[MessageRequest]

    metadata: Optional[dict[str, Any]]
    send_callback_response: Optional[bool]


class MessageResponseBody(BaseModel):
    success: bool
    detail: Optional[str]
    data: Optional[list[dict[str, Any]]]


class MessageResponse(BaseModel):
    source_message: Message
    body: MessageResponseBody
