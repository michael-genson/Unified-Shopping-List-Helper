import json
from typing import Any

from ..skill import aws_session

secrets = aws_session.client("secretsmanager")


class SecretsManager:
    @staticmethod
    def get_secrets(secret_id: str) -> dict[str, Any]:
        """Fetches secrets from AWS secrets manager"""

        response = secrets.get_secret_value(SecretId=secret_id)
        return json.loads(response["SecretString"])
