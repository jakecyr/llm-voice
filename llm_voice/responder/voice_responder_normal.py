"""Define the computer voice responder concrete class."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from llm_voice.errors.respond_error import RespondError
from llm_voice.responder.responder import Responder
from llm_voice.utils.mp3_file import Mp3File
from llm_voice.utils.logger import logger

if TYPE_CHECKING:
    from llm_voice.interfaces.audio_device import AudioDevice
    from llm_voice.tts.base import TextToSpeechClient


class VoiceResponder(Responder):
    """Responder that responds to the user with the Computer Voice."""

    def __init__(
        self,
        text_to_speech_client: TextToSpeechClient,
        output_device: AudioDevice,
        audio_filename: str = "speech.mp3",
        speech_rate: float = 1.0,
    ) -> None:
        """Initialize the ComputerVoiceResponder.

        Args:
            text_to_speech_client: The text to speech client.
            output_device: The output device to speak to the user on.
            audio_filename: The audio filename.
            speech_rate: The speech rate.
        """
        self._text_to_speech_client: TextToSpeechClient = text_to_speech_client
        self._speech_rate: float = speech_rate
        self.output_device: AudioDevice = output_device
        self._audio_filename_path: Path = Path.cwd() / (
            audio_filename + self._text_to_speech_client.audio_extension
        )

    def generate(self, text_to_speak: str) -> None:
        """Speak the referenced text on the machine speakers.

        Args:
            text_to_speak: The text to speak.
        """
        try:
            logger.debug(f"VoiceResponder.generate - '{text_to_speak}'")
            self._text_to_speech_client.convert_text_to_audio(
                text_to_speak,
                self._audio_filename_path,
            )
        except Exception as e:
            raise RespondError(f"Error generating computer voice response: {e}") from e

    def respond(self, text_to_speak: str) -> None:
        """Speak the referenced text on the machine speakers.

        Args:
            text_to_speak: The text to speak.
        """
        mp3_file: Mp3File | None = None

        try:
            logger.debug(f"VoiceResponder.respond - '{text_to_speak}'")

            if not self._audio_filename_path.exists():
                self._text_to_speech_client.convert_text_to_audio(
                    text_to_speak,
                    self._audio_filename_path,
                )

            mp3_file = Mp3File(self._audio_filename_path)
            mp3_file.play()
        except Exception as e:
            raise RespondError(f"Error running computer voice response: {e}") from e
        finally:
            if mp3_file:
                mp3_file.remove()
