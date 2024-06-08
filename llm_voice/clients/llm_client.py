"""Module for interacting with the OpenAI API."""

import abc
from dataclasses import dataclass
from enum import Enum
from typing import Any

from langchain.llms.base import LLM


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
    def get_function_to_call(
        self,
        *,
        functions: list[dict],
        messages: list[ChatMessage],
    ) -> tuple[str, dict] | None:
        """Get the function to call or none if there is no function to call.

        Args:
            functions: The list of functions defined.
            messages: The list of input messages.

        Returns:
            The function to call with args or none if there is no function to call.
        """

    @abc.abstractmethod
    def generate_chat_completion(
        self,
        user_prompt: str,
        *,
        temperature: float = 0.5,
    ) -> str | None:
        """Generate a chat completion.

        Args:
            user_prompt: The user prompt to generate the chat completion from.
            temperature: The temperature to use for the model.

        Returns:
            The response from the model.
        """


class LangChainLLMClientWrapper(LLM):
    llm_client: LLMClient

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: list[str] | None = None,
        run_manager: Any | None = None,
        **kwargs: Any,
    ):
        return self.llm_client.generate_chat_completion(prompt)
