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
        """Lightweight validation: ensure response contains result xor error."""
        if self.result is None and self.error is None:
            raise ValueError("Response must contain either 'result' or 'error'")
        if self.result is not None and self.error is not None:
            raise ValueError("Response must not contain both 'result' and 'error'")


class JSONRPCNotification(JSONRPCRequest):
    id: Optional[Union[int, str]] = None
