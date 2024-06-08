"""Module for interacting with the OpenAI API."""

from typing import Any, Iterator, Mapping
from llm_voice.llm.base import ChatMessage, LLMClient, MessageRole
import ollama
from ollama import Message as OllamaMessage


class OllamaClient(LLMClient):
    """Client for interacting with the Ollama Client."""

    def __init__(self, model_name: str = "llama3") -> None:
        """Initialize the OllamaClient instance."""
        self._model: str = model_name

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
        ollama_messages: list[OllamaMessage] = (
            self._from_chat_messages_to_open_ai_chat_messages(messages)
        )
        response: Mapping[str, Any] = ollama.chat(  # type:ignore
            messages=ollama_messages,
            model=self._model,
        )
        return response["message"]["content"]

    def generate_chat_completion_stream(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.5,
    ) -> Iterator[str]:
        """Generate a chat completion stream.

        Args:
            messages: The list of input messages.
            temperature: The temperature to use for the model.

        Returns:
            The stream response from the model.
        """
        ollama_messages: list[OllamaMessage] = (
            self._from_chat_messages_to_open_ai_chat_messages(messages)
        )
        response: Iterator[Mapping[str, Any]] = ollama.chat(  # type:ignore
            messages=ollama_messages, model=self._model, stream=True
        )

        for message in response:
            if message["message"]["content"] is not None:
                yield message["message"]["content"]

    def _from_chat_messages_to_open_ai_chat_messages(
        self,
        messages: list[ChatMessage],
    ) -> list[OllamaMessage]:
        return [
            self._from_chat_message_to_open_ai_chat_message(message)
            for message in messages
        ]

    def _from_chat_message_to_open_ai_chat_message(
        self,
        message: ChatMessage,
    ) -> OllamaMessage:
        if message.role == MessageRole.SYSTEM:
            return OllamaMessage(
                role="system",
                content=message.content,
            )

        if message.role == MessageRole.ASSISTANT:
            return OllamaMessage(
                role="assistant",
                content=message.content,
            )

        if message.role == MessageRole.USER:
            return OllamaMessage(
                role="user",
                content=message.content,
            )

        raise ValueError(f"Unknown message role: {message.role}")
