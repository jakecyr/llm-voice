from llm_voice.audio_devices import AudioDevices
from llm_voice.clients.apple_say_text_to_speech_client import AppleSayTextToSpeechClient
from llm_voice.computer_voice_responder import ComputerVoiceResponder
from llm_voice.env import MODEL_NAME
from llm_voice.interfaces.audio_device import AudioDevice, AudioDeviceType
import ollama


def main() -> None:
    """Run the main program."""
    devices: list[AudioDevice] = AudioDevices.get_list_of_devices(
        device_type=AudioDeviceType.OUTPUT
    )
    output_device: AudioDevice = devices[0]
    tts_client = AppleSayTextToSpeechClient()

    chat_stream = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": "Hello there, how are you today?"}],
        stream=True,
    )
    computer_voice_responder = ComputerVoiceResponder(
        text_to_speech_client=tts_client,
        output_device=output_device,
    )
    computer_voice_responder.speak_fast(chat_stream)


if __name__ == "__main__":
    main()
