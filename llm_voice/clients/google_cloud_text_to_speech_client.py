"""Define the GoogleTextToSpeechClient class.

The setup if a bit involved to use this client. The rough process
can be seen below:

1. Create a new project on the Google Cloud Platform console.
2. Enable the Text to Speech API (https://cloud.google.com/text-to-speech).
3. Install the Google Cloud CLI (https://cloud.google.com/sdk/docs/install).
4. Setup default account credentials (JSON file):
    * gcloud auth application-default login).
    * https://cloud.google.com/docs/authentication/provide-credentials-adc
5. You might need to set a quota project if you don't have one already.
    * gcloud auth application-default set-quota-project <PROJECT_ID>
5. Set the env variable GOOGLE_APPLICATION_CREDENTIALS to the path of the JSON file.
"""

from pathlib import Path

from google.cloud import texttospeech

from llm_voice.interfaces.text_to_speech_client import TextToSpeechClient
from llm_voice.utils.logger import logger


class GoogleCloudTextToSpeechClient(TextToSpeechClient):
    """Google Text to Speech API Client that converts a string to a mp3 file."""

    audio_extension = ".mp3"

    def __init__(self) -> None:
        """Create a new GoogleTextToSpeechClient instance."""

    def convert_text_to_audio(
        self,
        text_to_speak: str,
        audio_file_path: str | Path,
        force=True,
    ) -> None:
        """Convert the given text to audio and saves it to the specified file path.

        Args:
            text_to_speak: The text to convert to audio.
            audio_file_path: The path to save the audio file.
            force: Whether to overwrite the file if it already exists.

        Raises:
            FileExistsError: If the audio file path already exists and force is false.
        """
        if isinstance(audio_file_path, str):
            audio_file_path = Path(audio_file_path)

        if audio_file_path.exists() and not force:
            raise FileExistsError(
                f"The audio file path already exists: {audio_file_path}",
            )

        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text_to_speak)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Standard-J",
            ssml_gender=texttospeech.SsmlVoiceGender.MALE,
        )
        audio_config = texttospeech.AudioConfig(
            speaking_rate=1.2,
            audio_encoding=texttospeech.AudioEncoding.MP3,
            effects_profile_id=["small-bluetooth-speaker-class-device"],
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response: texttospeech.SynthesizeSpeechResponse = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        # The response's audio_content is binary.
        with audio_file_path.open("wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            logger.info(f'Audio content written to file "{audio_file_path}"')
