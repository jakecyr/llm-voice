"""Module for interacting with the OpenAI API."""

from langchain.llms.ollama import Ollama
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.prompts import PromptTemplate

from llm_voice.clients.llm_client import ChatMessage, LLMClient
from llm_voice.utils.logger import logger


class OllamaClient(LLMClient):
    """Client for interacting with the Ollama Client."""

    def __init__(self, model_name: str = "mistral") -> None:
        """Initialize the OllamaClient instance."""
        self._model = model_name
        self._ollama_client = Ollama(model=self._model, verbose=True)

    def get_function_to_call(
        self,
        *,
        functions: list[dict],
        messages: list[ChatMessage],
    ) -> tuple[str, dict] | None:
        """Get the function to call.

        Args:
            functions: The list of functions defined.
            messages: The list of input messages.

        Returns:
            The response from the API in dictionary format.
        """
        if not functions:
            raise ValueError("No functions defined")

        if not messages or len(messages) == 0:
            raise ValueError("No messages defined")

        logger.debug(
            f"Generating reasoning for functions: {functions} and messages: {messages}",
        )

        reasoning_template = PromptTemplate.from_template(
            template="""Given the user request below, determine which function could satisfy it.
            If it is a general question or comment and you cannot find a specific function,
            state that there is no function to call. Respond concisely with reasoning.

            Functions:
            {functions}

            <user_message>
            {user_message}
            </user_message>

            Function to call reasoning:""",
        )

        json_template = PromptTemplate.from_template(
            template="""Given the information below return JSON for the function to call.
            Return the function name along with the arguments in JSON format.
            Return it as JSON with the key "function_name" and "args".
            "args" should be a dictionary with the keys being the argument names and
            the values being the argument values.
            If not function was found to satisfy the request, return null for both keys.
            DO NOT ESCAPE UNDERSCORES.

            Function to call reasoning:
            {reasoning}
            </user_message>

            Function to call JSON:""",
        )

        chain = (
            {"reasoning": reasoning_template}
            | json_template
            | self._ollama_client
            | SimpleJsonOutputParser()
        )

        response = chain.invoke(
            {"user_message": messages[-1].content, "functions": functions},
        )

        print(response)

        if response is None:
            return None

        if "function_name" in response and "args" in response:
            return response["function_name"], response["args"]

        logger.warning(f"Ollama function calling return invalid JSON: {response}")
        return None

    def generate_chat_completion(
        self,
        user_prompt: str,
        *,
        temperature: float = 0.5,
    ) -> str | None:
        """Generate a chat completion.

        Args:
            user_prompt: The user prompt to generate the chat completion from.
            model: The model to use for the API.
            temperature: The temperature to use for the model.

        Returns:
            The response from the model.
        """
        response: str = self._ollama_client.invoke(
            input=user_prompt,
            model=self._model,
            temperature=temperature,
        )
        return response
