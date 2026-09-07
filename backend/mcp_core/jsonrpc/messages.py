from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel


class JSONRPCErrorObject(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


class JSONRPCRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    method: str
    params: Optional[Union[Dict[str, Any], List[Any]]] = None
    id: Optional[Union[int, str]] = None


class JSONRPCResponse(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: Optional[Union[int, str]]
    result: Optional[Any] = None
    error: Optional[JSONRPCErrorObject] = None

    def validate(self) -> None:
        """Validate result/error exclusivity, including a valid null result."""
        fields = getattr(self, "__fields_set__", set())
        has_result = "result" in fields
        has_error = "error" in fields
        if has_result == has_error:
            raise ValueError("Response must contain either 'result' or 'error'")


class JSONRPCNotification(JSONRPCRequest):
    id: Optional[Union[int, str]] = None
