from typing import Iterator
from llm_voice.utils.audio_devices import AudioDevices
from llm_voice.llm.base import ChatMessage, LLMClient, MessageRole
from llm_voice.llm.ollama_client import OllamaClient
from llm_voice.tts.openai_text_to_speech_client import OpenAITextToSpeechClient
from llm_voice.responder.voice_responder_fast import VoiceResponderFast
from llm_voice.env import MODEL_NAME
from llm_voice.interfaces.audio_device import AudioDevice, AudioDeviceType
from llm_voice.tts.base import TextToSpeechClient


def main() -> None:
    """Run the main program."""
    # Setup output device, TTS client and LLM client.
    devices: list[AudioDevice] = AudioDevices.get_list_of_devices(
        device_type=AudioDeviceType.OUTPUT
    )

    # Pick the first output device (usually computer builtin speakers if nothing else if connected).
    output_device: AudioDevice = devices[0]

    # Change to another TTS client depending on your needs and desires.
    tts_client: TextToSpeechClient = OpenAITextToSpeechClient()

    # Change to another LLM client depending on your needs and desires.
    llm_client: LLMClient = OllamaClient(
        model_name=MODEL_NAME,
    )

    # Define messages to send to the LLM.
    messages: list[ChatMessage] = [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content="You are a helpful assistant named Alfred.",
        ),
        ChatMessage(role=MessageRole.USER, content="Hey there what is your name?"),
    ]

    # Use the LLM to generate a response.
    chat_stream: Iterator[str] = llm_client.generate_chat_completion_stream(
        messages=messages,
    )

    # Create the voice responder and speak the response.
    voice_responder_fast = VoiceResponderFast(
        text_to_speech_client=tts_client,
        output_device=output_device,
    )
    voice_responder_fast.respond(chat_stream)


if __name__ == "__main__":
    main()
