"""Minimal JSON-RPC 2.0 helpers for Phase 1.

This package provides models, error helpers and simple parsing/serialization utilities.
"""
from .messages import JSONRPCErrorObject, JSONRPCNotification, JSONRPCRequest, JSONRPCResponse
from .errors import (
    PARSE_ERROR,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    INVALID_PARAMS,
    INTERNAL_ERROR,
    make_error_object,
)
from .utils import generate_id, parse_message, serialize_message

__all__ = [
    "JSONRPCRequest",
    "JSONRPCResponse",
    "JSONRPCNotification",
    "JSONRPCErrorObject",
    "PARSE_ERROR",
    "INVALID_REQUEST",
    "METHOD_NOT_FOUND",
    "INVALID_PARAMS",
    "INTERNAL_ERROR",
    "make_error_object",
    "generate_id",
    "parse_message",
    "serialize_message",
]
