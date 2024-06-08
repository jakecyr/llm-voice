from llm_voice.audio_devices import AudioDevices
from llm_voice.clients.apple_say_text_to_speech_client import AppleSayTextToSpeechClient
from llm_voice.computer_voice_responder import ComputerVoiceResponder
from llm_voice.env import MODEL_NAME
from llm_voice.interfaces.audio_device import AudioDevice, AudioDeviceType
import ollama
import threading
import queue
import time
import tempfile


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

    def worker(q: queue.Queue[str]) -> None:
        while True:
            item: str = q.get()
            if item is None:
                break

            print(f"Processing item: {item}")

            with tempfile.NamedTemporaryFile(suffix=".mp3") as audio_file:
                audio_filename: str = audio_file.name
                voice = ComputerVoiceResponder(
                    text_to_speech_client=tts_client,
                    audio_filename=audio_filename,
                    output_device=output_device,
                )
                voice.generate(item)

            time.sleep(1)
            q.task_done()

    sentence: str = ""
    q = queue.Queue[str]()
    thread = threading.Thread(target=worker, args=(q,))
    thread.start()

    for chat_message in chat_stream:
        current_text: str = chat_message["message"]["content"]
        sentence += current_text

        if current_text.strip() in {".", "!", "?"}:
            q.put(sentence)
            sentence = ""


if __name__ == "__main__":
    main()
