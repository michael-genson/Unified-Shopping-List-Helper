from typing import Any, Optional

from pydantic import BaseModel


class CallbackEvent(BaseModel):
    event_source: str
    event_id: str
    data: str
