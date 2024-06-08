from llm_voice.audio_devices import AudioDevices
from llm_voice.clients.apple_say_text_to_speech_client import AppleSayTextToSpeechClient
from llm_voice.computer_voice_responder import ComputerVoiceResponder
from llm_voice.env import MODEL_NAME
from llm_voice.interfaces.audio_device import AudioDevice, AudioDeviceType
import ollama
import threading
import queue
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

    lock = threading.Lock()

    def generate_worker(generate_queue: queue.Queue[str], speak_queue: queue.Queue[str]) -> None:
        while True:
            item: str = generate_queue.get()
            if item is None:
                break

            print(f"Generating audio for item: {item}")

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as audio_file:
                audio_filename: str = audio_file.name
                voice = ComputerVoiceResponder(
                    text_to_speech_client=tts_client,
                    audio_filename=audio_filename,
                    output_device=output_device,
                )
                voice.generate(item)

            speak_queue.put(audio_filename)
            generate_queue.task_done()

    def speak_worker(speak_queue: queue.Queue[str]) -> None:
        while True:
            audio_filename: str = speak_queue.get()
            if audio_filename is None:
                break

            print(f"Playing audio: {audio_filename}")

            voice = ComputerVoiceResponder(
                text_to_speech_client=tts_client,
                audio_filename=audio_filename,
                output_device=output_device,
            )

            with lock:
                voice.speak()

            speak_queue.task_done()

    sentence: str = ""
    generate_queue = queue.Queue[str]()
    speak_queue = queue.Queue[str]()
    generate_thread = threading.Thread(target=generate_worker, args=(generate_queue, speak_queue))
    speak_thread = threading.Thread(target=speak_worker, args=(speak_queue,))
    generate_thread.start()
    speak_thread.start()

    for chat_message in chat_stream:
        current_text: str = chat_message["message"]["content"]
        sentence += current_text

        if current_text.strip() in {".", "!", "?"}:
            generate_queue.put(sentence)
            sentence = ""

    generate_queue.put(None)
    generate_thread.join()
    speak_queue.put(None)
    speak_thread.join()


if __name__ == "__main__":
    main()
