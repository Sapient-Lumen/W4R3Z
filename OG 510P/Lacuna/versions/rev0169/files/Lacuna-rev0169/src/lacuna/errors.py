from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LacunaError(Exception):
    code: str
    message: str
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def receipt(self, *, before_head: str | None = None, operation_index: int | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {
            "event": "lacuna.change.refused",
            "schema": "lacuna.refusal.v1",
            "overall_status": "refused",
            "code": self.code,
            "message": self.message,
        }
        if before_head is not None:
            body["before_head"] = before_head
        if operation_index is not None:
            body["operation_index"] = operation_index
        if self.details:
            body["details"] = self.details
        return body
