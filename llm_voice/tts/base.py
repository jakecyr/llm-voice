"""Define the interface for text to speech clients."""

from abc import ABC, abstractmethod
from pathlib import Path


class TextToSpeechClient(ABC):
    """Interface for text to speech clients."""

    audio_extension: str

    @abstractmethod
    def convert_text_to_audio(
        self,
        text_to_speak: str,
        audio_file_path: Path,
        force: bool = True,
    ) -> None:
        """Convert the given text to audio and save it to the specified file path.

        Args:
            text_to_speak: The text to convert to audio.
            audio_file_path: The path to save the audio file.
            force: Whether to overwrite the file if it already exists.
        """
