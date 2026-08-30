from typing import Any, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

DataType = TypeVar("DataType")


class APIResponse(BaseModel, Generic[DataType]):
    """
    Standard successful HTTP API response format.
    """
    model_config = ConfigDict(extra="ignore")

    success: bool = Field(default=True, description="Whether the request succeeded")
    message: str = Field(default="Success", description="Human readable response message")
    data: DataType | None = Field(default=None, description="Response payload data")


class ErrorResponse(BaseModel):
    """
    Standard RFC 7807 problem details error response format.
    """
    model_config = ConfigDict(extra="ignore")

    type: str = Field(
        default="about:blank",
        description="URI reference identifying the problem type",
    )
    title: str = Field(..., description="Short, human-readable summary of the problem")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Human-readable explanation specific to this occurrence")
    instance: str | None = Field(
        default=None,
        description="URI reference identifying the specific occurrence of the problem",
    )
    errors: list[dict[str, Any]] | None = Field(
        default=None,
        description="Optional list of validation error details",
    )
