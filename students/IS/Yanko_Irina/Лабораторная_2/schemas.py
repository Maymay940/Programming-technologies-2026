from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, field_validator

Category = Literal["borrow", "renew", "availability", "other"]

class ExtractedData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: Category
    summary: str
    book_code: str | None
    reader_card: str | None
    requested_period: str | None
    details: str | None

    @field_validator("summary")
    @classmethod
    def check_summary(cls, value):
        if not value.strip():
            raise ValueError("summary не должен быть пустым")
        return value.strip()

    @field_validator("book_code", "reader_card","requested_period", "details")
    @classmethod
    def normalize_nullable(cls, value):
        if isinstance(value, str):
            return value.strip() or None
        return value

class MessageInput(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def check_message(cls, value):
        if not value.strip():
            raise ValueError("Сообщение не должно быть пустым")
        return value.strip()

class RequestOutput(ExtractedData):
    id: int
    created_at: datetime
    original_text: str
    book_id: int | None
    match_status: Literal["matched", "not_found", "not_provided"]