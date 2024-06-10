from enum import Enum


class MessageContentFilter(Enum):
    AUDIO = "audio"
    DOCUMENT = "document"
    IMAGE = "image"
    TEXT = "text"
    DEFAUlT = "default"
