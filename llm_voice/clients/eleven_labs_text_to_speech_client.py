"""Define the ElevenLabsTextToSpeechClient class."""

import json
import os
from pathlib import Path

import requests

from llm_voice.interfaces.text_to_speech_client import TextToSpeechClient
from llm_voice.utils.logger import logger

# Matilda voice.
DEFAULT_VOICE_ID = "XrExE9yKIg1WjnnlVkGX"


class ElevenLabsTextToSpeechClient(TextToSpeechClient):
    """Eleven Labs Text to Speech API Client that converts a string to a mp3 file."""

    audio_extension = ".mp3"

    def __init__(
        self,
        api_key: str | None = None,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",
    ) -> None:
        """Create a new ElevenLabsTextToSpeechClient instance."""
        if api_key is None:
            api_key = os.environ.get("ELEVEN_LABS_API_KEY")

        if api_key is None:
            raise ValueError(
                "Expected api_key parameter or ELEVEN_LABS_API_KEY env var to be set.",
            )

        self._api_key: str = api_key
        self._voice_id: str = voice_id

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

        response: requests.Response = requests.post(
            url=f"https://api.elevenlabs.io/v1/text-to-speech/{self._voice_id}?optimize_streaming_latency=1",
            timeout=10,
            headers={
                "xi-api-key": self._api_key,
                "Content-Type": "application/json",
                "accept": "audio/mpeg",
            },
            json={
                "text": text_to_speak,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0,
                    "similarity_boost": 0,
                },
            },
        )

        # The response's audio_content is binary.
        with audio_file_path.open("wb") as out:
            # Write the response to the output file.
            out.write(response.content)
            logger.info(f'Audio content written to file "{audio_file_path}"')

    def get_voices(self) -> dict:
        response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": self._api_key},
            timeout=5,
        )

        response_json: dict = json.loads(response.content)

        return response_json
