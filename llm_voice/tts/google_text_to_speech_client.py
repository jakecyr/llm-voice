"""Define the GoogleTextToSpeechClient class."""

from pathlib import Path

import gtts

from llm_voice.tts.base import TextToSpeechClient
from llm_voice.utils.logger import logger


class GoogleTextToSpeechClient(TextToSpeechClient):
    """Google Text to Speech API Client that converts a string to a mp3 file."""

    audio_extension = ".mp3"

    def __init__(
        self,
        output_language: str = "en",
        output_top_level_domain: str = "com",
    ) -> None:
        """Create a new GoogleTextToSpeechClient instance."""
        self._output_language: str = output_language
        self._output_top_level_domain: str = output_top_level_domain

    def convert_text_to_audio(
        self,
        text_to_speak: str,
        audio_file_path: str | Path,
        force: bool = True,
    ) -> None:
        """Convert the given text to audio and saves it to the specified file path.

        Args:
            text_to_speak: The text to convert to audio.
            audio_file_path: The path to save the audio file.
            force: Whether to overwrite the file if it already exists.

        Raises:
            FileExistsError: If the audio file path already exists.
        """
        if isinstance(audio_file_path, str):
            audio_file_path = Path(audio_file_path)

        if audio_file_path.exists() and not force:
            raise FileExistsError(
                f"The audio file path already exists: {audio_file_path}",
            )

        tts: gtts.gTTS = self._get_gtts(text_to_speak)
        tts.save(audio_file_path)

    def _get_gtts(self, text_to_speak: str) -> gtts.gTTS:
        """Return a gtts.gTTS object that generates speech from the given text.

        Args:
            text_to_speak: The text to be converted into speech.

        Returns:
            gtts.gTTS: The gtts.gTTS object that generates speech from the text.
        """
        if (
            self._output_language is not None
            and self._output_top_level_domain is not None
        ):
            logger.debug(
                f"GTTS Using language: {self._output_language} "
                f"({self._output_top_level_domain})",
            )
            return self._get_lang_gtts(text_to_speak)

        logger.debug("GTTS Using default language")
        return gtts.gTTS(text_to_speak)

    def _get_lang_gtts(self, text_to_speak: str) -> gtts.gTTS:
        """Create a gTTS object for the given text to speak in the specified language.

        Args:
            text_to_speak: The text to be converted into speech.

        Returns:
            The gTTS object created for the given text.

        Raises:
            AssertionError: If the text to speak is empty before or after cleaning.
            ValueError: If the specified language is not supported.
            RuntimeError: If the language dictionaries for the specified language cannot
                be loaded.
        """
        try:
            lang_gtts = gtts.gTTS(
                text_to_speak,
                lang=self._output_language,
                tld=self._output_top_level_domain,
            )

        except AssertionError:
            logger.error(
                f"Text to speak, '{text_to_speak}', can not be empty "
                "(before or after cleaning)",
            )
            raise
        except ValueError:
            logger.error(f"Specified lang, '{self._output_language}', is not supported")
            raise
        except RuntimeError:
            logger.error(
                f"Unable to load language dictionaries for language "
                f"'{self._output_language}'",
            )
            raise
        else:
            return lang_gtts
