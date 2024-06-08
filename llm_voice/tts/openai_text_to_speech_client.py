"""Define the ElevenLabsTextToSpeechClient class."""

import os
from pathlib import Path
from typing import Literal

from openai import OpenAI
from openai._legacy_response import HttpxBinaryResponseContent

from llm_voice.tts.base import TextToSpeechClient

DEFAULT_MODEL = "tts-1"


class OpenAITextToSpeechClient(TextToSpeechClient):
    """Eleven Labs Text to Speech API Client that converts a string to a mp3 file."""

    audio_extension = ".mp3"

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "nova",
        api_key: str | None = None,
    ) -> None:
        """Create a new OpenAITextToSpeechClient instance."""
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")

        if api_key is None:
            raise ValueError(
                "Expected api_key parameter or OPENAI_API_KEY env var to be set.",
            )

        self._api_key: str = api_key
        self._model: str = model
        self._voice: Literal[
            "alloy",
            "echo",
            "fable",
            "onyx",
            "nova",
            "shimmer",
        ] = voice

    def convert_text_to_audio(
        self,
        text_to_speak: str,
        audio_file_path: str | Path,
        force=True,
    ) -> None:
        """Convert the given text to audio and saves it to the specified file path.

        Args:
            text_to_speak: The text to convert to audio.
            audio_file_path: The path to save the audio file.
            force: Whether to overwrite the file if it already exists.

        Raises:
            FileExistsError: If the audio file path already exists and force is false.
        """
        if isinstance(audio_file_path, str):
            audio_file_path = Path(audio_file_path)

        if audio_file_path.exists() and not force:
            raise FileExistsError(
                f"The audio file path already exists: {audio_file_path}",
            )

        client = OpenAI(api_key=self._api_key)

        response: HttpxBinaryResponseContent = client.audio.speech.create(
            model=self._model,
            voice=self._voice,
            input=text_to_speak,
        )

        response.stream_to_file(audio_file_path)
