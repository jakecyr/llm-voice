"""Define the computer voice responder concrete class."""

from __future__ import annotations

from pathlib import Path
import queue
import tempfile
import threading
from typing import TYPE_CHECKING

from llm_voice.errors.respond_error import RespondError
from llm_voice.interfaces.responder import Responder
from llm_voice.mp3_file import Mp3File
from llm_voice.utils.logger import logger

if TYPE_CHECKING:
    from llm_voice.interfaces.audio_device import AudioDevice
    from llm_voice.interfaces.text_to_speech_client import TextToSpeechClient


class ComputerVoiceResponder(Responder):
    """Responder that responds to the user with the Computer Voice."""

    def __init__(
        self,
        text_to_speech_client: TextToSpeechClient,
        audio_filename: str,
        output_device: AudioDevice,
        speech_rate: float = 1.0,
    ) -> None:
        """Initialize the ComputerVoiceResponder.

        Args:
            text_to_speech_client: The text to speech client.
            audio_filename: The audio filename.
            output_device: The output device to speak to the user on.
            speech_rate: The speech rate.
        """
        self._text_to_speech_client: TextToSpeechClient = text_to_speech_client
        self._audio_filename: Path = Path.cwd() / (
            audio_filename + self._text_to_speech_client.audio_extension
        )
        self._speech_rate: float = speech_rate
        self.output_device: AudioDevice = output_device

    def generate(self, text_to_speak: str) -> None:
        """Speak the referenced text on the machine speakers.

        Args:
            text_to_speak: The text to speak.
        """
        try:
            logger.debug(f"ComputerVoiceResponder.speak - '{text_to_speak}'")
            self._text_to_speech_client.convert_text_to_audio(
                text_to_speak,
                self._audio_filename,
            )
        except Exception as e:
            raise RespondError(f"Error running computer voice response: {e}") from e

    def speak(self) -> None:
        """Speak the referenced text on the machine speakers."""
        mp3_file = Mp3File(self._audio_filename)

        try:
            mp3_file.play()
        except Exception as e:
            raise RespondError(f"Error playing computer voice response: {e}") from e

        mp3_file.remove()

    def speak_fast(self, chat_stream) -> None:
        self.lock = threading.Lock()

        sentence: str = ""
        generate_queue = queue.Queue[str]()
        speak_queue = queue.Queue[str]()
        generate_thread = threading.Thread(
            target=self._generate_worker, args=(generate_queue, speak_queue)
        )
        speak_thread = threading.Thread(target=self._speak_worker, args=(speak_queue,))
        generate_thread.start()
        speak_thread.start()

        for chat_message in chat_stream:
            current_text: str = chat_message["message"]["content"]
            sentence += current_text

            if current_text.strip() in {".", "!", "?"}:
                generate_queue.put(sentence)
                sentence = ""

        generate_queue.put(None)
        generate_thread.join()
        speak_queue.put(None)
        speak_thread.join()

    def _generate_worker(
        self, generate_queue: queue.Queue[str], speak_queue: queue.Queue[str]
    ) -> None:
        while True:
            item: str = generate_queue.get()
            if item is None:
                break

            print(f"Generating audio for item: {item}")

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as audio_file:
                audio_filename: str = audio_file.name
                voice = ComputerVoiceResponder(
                    text_to_speech_client=self._text_to_speech_client,
                    audio_filename=audio_filename,
                    output_device=self.output_device,
                )
                voice.generate(item)

            speak_queue.put(audio_filename)
            generate_queue.task_done()

    def _speak_worker(self, speak_queue: queue.Queue[str]) -> None:
        while True:
            audio_filename: str = speak_queue.get()
            if audio_filename is None:
                break

            print(f"Playing audio: {audio_filename}")

            voice = ComputerVoiceResponder(
                text_to_speech_client=self._text_to_speech_client,
                audio_filename=audio_filename,
                output_device=self.output_device,
            )

            with self.lock:
                voice.speak()

            speak_queue.task_done()
