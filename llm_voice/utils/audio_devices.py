"""Define the audio device objects."""

from typing import cast

from pyaudio import PyAudio

from llm_voice.interfaces.audio_device import AudioDevice, AudioDeviceType
from llm_voice.interfaces.pyaudio_device_info import PyAudioDeviceInfo
from llm_voice.utils.logger import logger


class AudioDevices:
    """Class to interact with the current machines audio devices."""

    @staticmethod
    def get_list_of_devices(
        device_type: AudioDeviceType | None = None,
    ) -> list[AudioDevice]:
        """Get a list of audio devices on the current machine.

        Args:
            device_type: The type of devices to get.

        Returns:
            List of audio device objects on the current machine.
        """
        logger.debug("AudioDevices.get_list_of_devices called")

        raw_audio_devices: list[PyAudioDeviceInfo] = AudioDevices._get_all_devices()
        audio_devices: list[AudioDevice] = []

        for raw_device in raw_audio_devices:
            current_device_type = AudioDeviceType.UNKNOWN

            if raw_device["maxInputChannels"] > 0:
                current_device_type = AudioDeviceType.INPUT

            if raw_device["maxOutputChannels"] > 0:
                if current_device_type == AudioDeviceType.INPUT:
                    current_device_type = AudioDeviceType.INPUT_OUTPUT
                else:
                    current_device_type = AudioDeviceType.OUTPUT

            if device_type is not None and current_device_type != device_type:
                continue

            device_index: int = cast(int, raw_device["index"])
            device_name: str = cast(str, raw_device["name"])
            audio_device = AudioDevice(
                index=device_index,
                name=device_name,
                device_type=current_device_type,
            )
            audio_devices.append(audio_device)

        logger.debug(f"Found {len(audio_devices)} devices.")
        return audio_devices

    @staticmethod
    def get_device_by_name(name: str) -> AudioDevice:
        """Get an audio device by name.

        Args:
            name: The name of the audio device.

        Returns:
            The audio device object.
        """
        devices: list[AudioDevice] = AudioDevices.get_list_of_devices()
        for device in devices:
            if device.name == name:
                return device

        raise ValueError(f"Device {name} not found.")

    @staticmethod
    def get_device_by_index(index: int) -> AudioDevice:
        """Get an audio device by index.

        Args:
            index: The index of the audio device.

        Returns:
            The audio device object.
        """
        return AudioDevices.get_list_of_devices()[index]

    @staticmethod
    def get_first_of_type(device_type: AudioDeviceType) -> AudioDevice:
        """Get the first audio device of the specified type.

        Args:
            device_type: The type of audio device.

        Returns:
            The audio device object.
        """
        return AudioDevices.get_list_of_devices(device_type)[0]

    @staticmethod
    def _get_all_devices() -> list[PyAudioDeviceInfo]:
        """Get a list of audio devices.

        Returns:
            A list of audio device objects.
        """
        py_audio = PyAudio()
        count_of_input_devices: int = py_audio.get_device_count()

        return [
            cast(PyAudioDeviceInfo, py_audio.get_device_info_by_index(device_index))
            for device_index in range(0, count_of_input_devices)
        ]
