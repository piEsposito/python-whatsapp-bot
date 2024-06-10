from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Callable

from bot_whatsapp.constants import COMMAND_START
from bot_whatsapp.filters import MessageContentFilter
from bot_whatsapp.models import WebhookEvent

if TYPE_CHECKING:
    from bot_whatsapp import Bot


class Handler:
    def __init__(
        self,
        filter_: "MessageContentFilter" | Callable[[WebhookEvent], bool] | None,
        handler: Callable[[WebhookEvent, "Bot"], Any],
    ):
        self.filter_ = filter_
        self.handler = handler

    @abstractmethod
    def verify(self, event: WebhookEvent) -> bool:
        raise NotImplementedError()


class CommandHandler(Handler):
    def verify(self, event: WebhookEvent) -> bool:
        text = event.entry[0].changes[0].value.messages[0].text
        if text is None:
            return False
        text_body = text.body
        if not text_body.startswith(COMMAND_START):
            return False
        return text.body.split(" ")[0] == f"{self.filter_}"


class MessageHandler(Handler):
    def verify(self, event: WebhookEvent) -> bool:
        messages = event.entry[0].changes[0].value.messages
        if messages is None:
            return False
        message = messages[0]
        # if filter is callable, call it on message
        if callable(self.filter_):
            return self.filter_(message)

        if self.filter_ == MessageContentFilter.DEFAUlT:
            return True

        # if filter is MessageContentFilter check if message has that content as not None
        if isinstance(self.filter_, MessageContentFilter):
            return message.dict().get(self.filter_.value) is not None

        return False
