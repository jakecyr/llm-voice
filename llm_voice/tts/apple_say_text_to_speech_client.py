"""Define the Apple Say TTS client."""

import subprocess
from pathlib import Path

from llm_voice.tts.base import TextToSpeechClient
from llm_voice.utils.logger import logger


class AppleSayTextToSpeechClient(TextToSpeechClient):
    """Apple 'say' TTS CLI client that generates an AIFF file."""

    audio_extension = ".aiff"

    def convert_text_to_audio(
        self,
        text_to_speak: str,
        audio_file_path: Path,
        force: bool = True,
    ) -> None:
        """Convert the given text to audio and saves it to the specified file path.

        Args:
            text_to_speak: The text to be converted to audio.
            audio_file_path: The path where the audio file will be saved.
            force: Whether to overwrite the file if it already exists.

        Raises:
            FileExistsError: If the audio file path already exists.
        """
        if audio_file_path.exists() and not force:
            raise FileExistsError(
                f"The audio file path already exists: {audio_file_path}",
            )

        cmd: list[str] = ["say", text_to_speak, "-o", str(audio_file_path)]
        logger.debug(cmd)
        subprocess.call(cmd)
