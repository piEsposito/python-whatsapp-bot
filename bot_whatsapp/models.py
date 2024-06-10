from typing import List, Literal

from pydantic import BaseModel, Field, validator


class Metadata(BaseModel):
    display_phone_number: str
    phone_number_id: str


class Text(BaseModel):
    body: str


class MediaType(BaseModel):
    mime_type: str | None = None
    id_: str = Field(..., alias="id")

    class Config:
        extra = "allow"


class Media(BaseModel):
    id_: str = Field(..., alias="id")
    caption: str | None = None
    sha256: str | None = None
    mime_type: str | None = None
    extension: str | None = None

    @validator("extension", pre=True, always=True)
    def set_extension(cls, v, values, **kwargs):
        if values.get("mime_type"):
            mime_type = values.get("mime_type")
            parts = mime_type.split(";")[0].split("/")
            extension = parts[1] if len(parts) > 1 else None
            return extension
        return None


class InputMessage(BaseModel):
    from_: str = Field(..., alias="from")
    id_: str = Field(..., alias="id")
    timestamp: str
    type_: str = Field(..., alias="type")
    text: Text | None = None
    audio: Media | None = None
    image: Media | None = None
    document: Media | None = None


class Profile(BaseModel):
    name: str


class Contact(BaseModel):
    profile: Profile
    wa_id: str


class Value(BaseModel):
    messaging_product: Literal["whatsapp"]
    metadata: Metadata
    messages: List[InputMessage] | None = None
    contacts: List[Contact] | None = None


class Change(BaseModel):
    value: Value
    field: Literal["messages"]

    class Config:
        extra = "allow"


class Entry(BaseModel):
    id: str
    changes: List[Change]


class WebhookEvent(BaseModel):
    object: Literal["whatsapp_business_account"]
    entry: List[Entry]


class OutputMessage(BaseModel):
    messaging_product: Literal["whatsapp"]
    to: str
    type: Literal["text"]
    text: Text
