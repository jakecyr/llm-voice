"""Define the Mp3File class."""

from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path

from llm_voice.errors.respond_error import RespondError
from llm_voice.utils.logger import logger


class Mp3File:
    """Responder that responds to the user with the Computer Voice."""

    def __init__(
        self,
        audio_filename: Path,
    ) -> None:
        """Initialize the Mp3File instance.

        Args:
            audio_filename: The audio filename.
        """
        self._audio_filename: Path = Path.cwd() / audio_filename

    def play(self) -> None:
        """Speak the referenced text on the machine speakers."""
        try:
            platform_name: str = platform.system().lower()
            logger.debug(f"Platform name: {platform_name}")

            if platform_name == "darwin":
                logger.debug("Trying to play mp3 on Mac...")

                cmd: list[str] = [
                    "afplay",
                    "--volume",
                    # 1=normal (default) and then up to 255=Very loud.
                    "1",
                    str(self._audio_filename),
                ]
                subprocess.call(cmd)
            elif platform_name == "win32" or platform_name == "cygwin":
                logger.debug("Trying to speak on Windows...")

                # TODO @JakeCyr: Test on Windows
                # https://gitlab.com/gpt-home-assistant/home-assistant-core/-/issues/29
                os.system(f"start {self._audio_filename}")  # noqa: S605
            else:
                # TODO @JakeCyr: Test on Windows
                # https://gitlab.com/gpt-home-assistant/home-assistant-core/-/issues/30
                logger.debug("Trying to speak on Linux...")
                cmd = [
                    "ffplay",
                    "-v",
                    "0",
                    "-nodisp",
                    "-autoexit",
                    str(self._audio_filename),
                ]
                subprocess.call(cmd)

        except Exception as e:
            raise RespondError(f"Error running computer voice response: {e}") from e

    def remove(self) -> None:
        """Remove the file."""
        self._audio_filename.unlink(missing_ok=True)
