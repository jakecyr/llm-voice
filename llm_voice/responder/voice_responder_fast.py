from __future__ import annotations

from pathlib import Path
import queue
import tempfile
import time
import threading
from typing import TYPE_CHECKING, Iterable

from llm_voice.errors.respond_error import RespondError
from llm_voice.utils.mp3_file import Mp3File
from llm_voice.utils.logger import logger

if TYPE_CHECKING:
    from llm_voice.interfaces.audio_device import AudioDevice
    from llm_voice.tts.base import TextToSpeechClient


class VoiceResponderFast:
    """Responder that responds to the user with the Computer Voice."""

    def __init__(
        self,
        text_to_speech_client: TextToSpeechClient,
        output_device: AudioDevice,
        speech_rate: float = 1.0,
    ) -> None:
        """Initialize the VoiceResponderFast.

        Args:
            text_to_speech_client: The text to speech client.
            output_device: The output device to speak to the user on.
            speech_rate: The speech rate.
        """
        self._text_to_speech_client: TextToSpeechClient = text_to_speech_client
        self._speech_rate: float = speech_rate
        self.output_device: AudioDevice = output_device

    def generate(self, audio_filename: str, text_to_speak: str) -> None:
        """Generate audio from text using text-to-speech client.

        Args:
            audio_filename: The filename to save the generated audio.
            text_to_speak: The text to generate audio for.
        """
        try:
            logger.debug(f"VoiceResponderFast.speak - '{text_to_speak}'")
            self._text_to_speech_client.convert_text_to_audio(
                text_to_speak,
                Path(audio_filename),
            )
        except Exception as e:
            raise RespondError(f"Error running computer voice response: {e}") from e

    def respond(self, text_to_speak: Iterable[str]) -> None:
        lock = threading.Lock()
        sentence: str = ""
        generate_queue = queue.Queue[str]()
        speak_queue = queue.Queue[str]()

        def generate_worker(
            generate_queue: queue.Queue[str], speak_queue: queue.Queue[str]
        ) -> None:
            while True:
                item: str = generate_queue.get()

                if item is None:
                    break

                # Create temp file with extension
                with tempfile.NamedTemporaryFile(
                    suffix=self._text_to_speech_client.audio_extension,
                    delete=False,
                ) as audio_file:
                    logger.debug(
                        f"VoiceResponderFast: Generating audio file ({audio_file.name}) for: '{item}'"
                    )
                    self.generate(audio_file.name, item)

                audio_file_path = Path(audio_file.name)

                while (
                    not audio_file_path.exists()
                    or not audio_file_path.is_file()
                    or audio_file_path.stat().st_size == 0
                ):
                    time.sleep(0.1)

                speak_queue.put(audio_file.name)
                generate_queue.task_done()

        def speak_worker(speak_queue: queue.Queue[str]) -> None:
            while True:
                audio_filename: str = speak_queue.get()
                if audio_filename is None:
                    break

                logger.debug(f"Playing audio: {audio_filename}")

                try:
                    mp3_file = Mp3File(Path(audio_filename))

                    logger.debug(
                        f"Playing audio: {audio_filename} on output device: {self.output_device}"
                    )

                    with lock:
                        mp3_file.play()
                except Exception as e:
                    raise RespondError(
                        f"Error playing computer voice response: {e}"
                    ) from e
                finally:
                    logger.debug(f"Deleting audio file: {audio_filename}")
                    Path(audio_filename).unlink(missing_ok=True)  # Remove the file

                speak_queue.task_done()

        generate_thread = threading.Thread(
            target=generate_worker, args=(generate_queue, speak_queue)
        )
        speak_thread = threading.Thread(target=speak_worker, args=(speak_queue,))
        generate_thread.start()
        speak_thread.start()

        for chat_message in text_to_speak:
            current_text: str = chat_message
            sentence += current_text

            if current_text.strip() in {".", "!", "?"}:
                generate_queue.put(sentence)
                sentence = ""

        generate_queue.put(None)  # type: ignore
        generate_thread.join()
        speak_queue.put(None)  # type: ignore
        speak_thread.join()
