from llm_voice.utils.audio_devices import AudioDevices
from llm_voice.llm.base import ChatMessage, LLMClient, MessageRole
from llm_voice.llm.ollama_client import OllamaClient
from llm_voice.responder.voice_responder_normal import VoiceResponder
from llm_voice.tts.apple_say_text_to_speech_client import AppleSayTextToSpeechClient
from llm_voice.env import MODEL_NAME
from llm_voice.interfaces.audio_device import AudioDevice, AudioDeviceType
from llm_voice.tts.base import TextToSpeechClient


def main() -> None:
    """Run the main program."""
    # Setup output device, TTS client and LLM client.
    devices: list[AudioDevice] = AudioDevices.get_list_of_devices(
        device_type=AudioDeviceType.OUTPUT
    )
    output_device: AudioDevice = devices[0]
    tts_client: TextToSpeechClient = AppleSayTextToSpeechClient()
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
    chat_response: str | None = llm_client.generate_chat_completion(
        messages=messages,
    )
    computer_voice_responder = VoiceResponder(
        text_to_speech_client=tts_client,
        output_device=output_device,
    )
    computer_voice_responder.respond(
        text_to_speak=chat_response or "No text returned from the LLM"
    )


if __name__ == "__main__":
    main()
