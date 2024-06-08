"""Module for interacting with the OpenAI API."""

import abc
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum


class ChatRole(str, Enum):
    """Enum representing the role options for a ChatCompletion input message."""

    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


class MessageRole(str, Enum):
    """Enum representing the role options for a ChatCompletion input message.

    Args:
        USER: The user role.
        ASSISTANT: The assistant role.
        SYSTEM: The system role.
    """

    __slots__ = ()
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    role: MessageRole
    content: str


class LLMClient(abc.ABC):
    """Client for interacting with an LLM."""

    @abc.abstractmethod
    def generate_chat_completion(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.5,
    ) -> str | None:
        """Generate a chat completion.

        Args:
            messages: The list of input messages.
            temperature: The temperature to use for the model.

        Returns:
            The response from the model.
        """

    @abc.abstractmethod
    def generate_chat_completion_stream(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.5,
    ) -> Iterator[str]:
        """Generate a chat completion.

        Args:
            messages: The list of input messages.
            temperature: The temperature to use for the model.

        Returns:
            The stream response from the model.
        """
