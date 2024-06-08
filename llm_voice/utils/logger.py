"""Define a common logger object to use throughout the project."""

import logging
import os
from logging import Logger, _nameToLevel, getLogger

from llm_voice.errors.invalid_log_level_error import InvalidLogLevelError

LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
LOG_FILE_PATH: str | None = os.environ.get("LOG_FILE_PATH")
LOG_LEVEL = LOG_LEVEL.upper()

if LOG_LEVEL not in _nameToLevel:
    raise InvalidLogLevelError(LOG_LEVEL)

logger: Logger = getLogger("llm_voice")
logger.setLevel(LOG_LEVEL)

# Create a handler that writes log messages to the console.
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)

# Create a formatter and set it for both handlers.
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Create a handler that writes log messages to a file.
if LOG_FILE_PATH:
    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
