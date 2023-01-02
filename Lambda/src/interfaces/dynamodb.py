import time
from math import ceil
from typing import Any, Optional

from dynamodb_json import json_util as ddb_json  # type: ignore

from ..skill import aws_session

ddb = aws_session.client("dynamodb")


class DynamoDB:
    """Provides higher-level functions to interact with DynamoDB"""

    def __init__(self, tablename: str, ttl_column: str = "expires") -> None:
        self.tablename = tablename
        self.ttl_column = ttl_column

    def _generate_ttl_timestamp(self, seconds: int, start: Optional[int] = None) -> int:
        """Generates a UNIX timestamp to expire an item after a certain amount of time"""

        start = start or ceil(time.time())
        return start + seconds

    def get(self, key: str, value: str) -> dict[str, Any]:
        """Gets a single item by primary key"""

        data = ddb.get_item(TableName=self.tablename, Key={key: {"S": value}})
        return ddb_json.loads(data["Item"])

    def put(self, item: dict[str, Any], expiration: Optional[int] = None) -> None:
        """Creates or updates a single item. Optionally set the expiration time in seconds"""

        if expiration:
            item[self.ttl_column] = self._generate_ttl_timestamp(expiration)

        ddb.put_item(TableName=self.tablename, Item=ddb_json.dumps(item, as_dict=True))
