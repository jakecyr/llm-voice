"""Module for interacting with the OpenAI API."""

import json
import os

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from llm_voice.clients.llm_client import ChatMessage, LLMClient, MessageRole
from llm_voice.utils.logger import logger


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
        model: str = "gpt-3.5-turbo-0125",
    ) -> None:
        """Initialize the OpenAIClient instance.

        Args:
            api_key: The OpenAI API key.
        """
        if not api_key and "OPENAI_API_KEY" not in os.environ:
            raise ValueError(
                "Expected api_key parameter or OPENAI_API_KEY env var to be set.",
            )

        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._openai_client = OpenAI(api_key=api_key)
        self._model = model

    def get_function_to_call(
        self,
        *,
        functions: list[dict],
        messages: list[ChatMessage],
    ) -> tuple[str, dict] | None:
        """Get the function to call or the response from the OpenAI ChatCompletion API.

        Args:
            functions: The list of functions defined.
            messages: The list of input messages.

        Returns:
            The response from the API in dictionary format.
        """
        if not functions:
            raise ValueError("Expected functions to be defined")

        if not messages or len(messages) == 0:
            raise ValueError("Expected there to be messages to send.")

        logger.debug(
            "Calling get_function_to_call with functions (OpenAI) "
            f"and model {self._model}, messages {messages}",
        )

        open_ai_chat_messages = self._from_chat_messages_to_open_ai_chat_messages(
            messages,
        )

        response = self._openai_client.chat.completions.create(
            model=self._model,
            messages=open_ai_chat_messages,  # type: ignore
            tools=functions,  # type: ignore
            tool_choice="auto",  # Auto is the default.
            temperature=0,
        )

        if len(response.choices) == 0:
            raise TextGenerationError(
                "No response received from the OpenAI chat completion API.",
            )

        if response.choices[0].message is None:
            raise TextGenerationError(
                "No response received from the OpenAI chat completion API.",
            )

        message = response.choices[0].message

        if len(message.tool_calls) == 0:
            return None

        tool_call = message.tool_calls[0]
        parsed_arguments = json.loads(tool_call.function.arguments)

        return tool_call.function.name, parsed_arguments

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
        open_ai_chat_completion_message = (
            self._from_chat_message_to_open_ai_chat_message(
                ChatMessage(role=MessageRole.USER, content=user_prompt),
            )
        )

        response = self._openai_client.chat.completions.create(
            model=self._model,
            messages=[open_ai_chat_completion_message],  # type: ignore
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

        message = response.choices[0].message
        return message.content

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
