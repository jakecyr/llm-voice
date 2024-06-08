"""Module for interacting with the OpenAI API."""

from collections.abc import Iterator
from openai import OpenAI, Stream
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat.chat_completion_function_message_param import (
    ChatCompletionFunctionMessageParam,
)
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.chat.chat_completion_tool_message_param import (
    ChatCompletionToolMessageParam,
)
from llm_voice.env import MODEL_NAME, OPENAI_API_KEY
from llm_voice.llm.base import ChatMessage, LLMClient, MessageRole


class TextGenerationError(Exception):
    """Exception raised for text generation errors."""


class OpenAIClient(LLMClient):
    """Client for interacting with the OpenAI API.

    Attributes
        api_key: The OpenAI API key.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = MODEL_NAME,
    ) -> None:
        """Initialize the OpenAIClient instance.

        Args:
            api_key: The OpenAI API key.
        """
        if not api_key and not OPENAI_API_KEY:
            raise ValueError(
                "Expected api_key parameter or OPENAI_API_KEY env var to be set.",
            )

        api_key = api_key or OPENAI_API_KEY
        self._openai_client = OpenAI(api_key=api_key)
        self._model: str = model

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
        open_ai_chat_completion_messages: list[
            ChatCompletionSystemMessageParam
            | ChatCompletionUserMessageParam
            | ChatCompletionAssistantMessageParam
            | ChatCompletionToolMessageParam
            | ChatCompletionFunctionMessageParam
        ] = self._from_chat_messages_to_open_ai_chat_messages(messages)

        response: ChatCompletion = self._openai_client.chat.completions.create(
            model=self._model,
            messages=open_ai_chat_completion_messages,
            temperature=temperature,
        )

        if len(response.choices) == 0:
            raise TextGenerationError(
                "No response received from the OpenAI chat completion API.",
            )

        if response.choices[0].message is None:
            raise TextGenerationError(
                "No response received from the OpenAI chat completion API.",
            )

        message: ChatCompletionMessage = response.choices[0].message
        return message.content

    def generate_chat_completion_stream(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.5,
    ) -> Iterator[str | None]:
        """Generate a chat completion.

        Args:
            messages: The list of input messages.
            temperature: The temperature to use for the model.

        Returns:
            The response from the model.
        """
        open_ai_chat_completion_messages: list[
            ChatCompletionSystemMessageParam
            | ChatCompletionUserMessageParam
            | ChatCompletionAssistantMessageParam
            | ChatCompletionToolMessageParam
            | ChatCompletionFunctionMessageParam
        ] = self._from_chat_messages_to_open_ai_chat_messages(messages)

        response: Stream[ChatCompletionChunk] = (
            self._openai_client.chat.completions.create(
                model=self._model,
                messages=open_ai_chat_completion_messages,
                temperature=temperature,
                stream=True,
            )
        )

        for chunk in response:
            if chunk.choices[0].delta is None:
                continue

            yield chunk.choices[0].delta.content

    def _from_chat_messages_to_open_ai_chat_messages(
        self,
        messages: list[ChatMessage],
    ) -> list[ChatCompletionMessageParam]:
        return [
            self._from_chat_message_to_open_ai_chat_message(message)
            for message in messages
        ]

    def _from_chat_message_to_open_ai_chat_message(
        self,
        message: ChatMessage,
    ) -> ChatCompletionMessageParam:
        if message.role == MessageRole.SYSTEM:
            return ChatCompletionSystemMessageParam(
                role=message.role.value,
                content=message.content,
            )

        if message.role == MessageRole.ASSISTANT:
            return ChatCompletionAssistantMessageParam(
                role=message.role.value,
                content=message.content,
            )

        if message.role == MessageRole.USER:
            return ChatCompletionUserMessageParam(
                role=message.role.value,
                content=message.content,
            )

        raise ValueError(f"Unknown message role: {message.role}")
