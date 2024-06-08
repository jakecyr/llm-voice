"""Define the audio device options data model."""

from dataclasses import dataclass
from enum import Enum, auto


class AudioDeviceType(Enum):
    """Type of audio device."""

    UNKNOWN = auto()
    INPUT = auto()
    OUTPUT = auto()
    INPUT_OUTPUT = auto()


@dataclass(frozen=True)
class AudioDevice:
    """Data model for an audio device option."""

    index: int
    name: str
    device_type: AudioDeviceType
