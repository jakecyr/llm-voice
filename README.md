# LLM Voice

Library to reduce latency in voice generations from LLM chat completion streams.

This lets you generate voices from streams of text from local LLMs, such as Ollama and local TTS clients, such as Apple Say along with external clients such as Google Text-to-Speech with the same speed as privately created assistants such as OpenAI.

As each sentence end is detected, it will run TTS on it and play it out loud while the rest of the completion is being generated in the background.

## Installation and Setup

1. Install the package from PyPI with:

   ```bash
   pip install llm-voice
   ```

2. Copy the .env.example file to .env and fill in your OpenAI API key if you want to use OpenAI along with the model name for the Ollama/OpenAI model you want to use.
3. Take a look at one of the examples to start generating voice responses in realtime.

## Example Usage

The example below can be found in the [examples](./examples/README.md) directory.

```python
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

# Will speak each sentence back to back as it is available.
voice_responder_fast.respond(chat_stream)
```

## Install From Source

```bash
pip install poetry
poetry install
```

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
