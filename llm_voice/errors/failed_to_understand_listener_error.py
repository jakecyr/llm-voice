"""Module for handling errors related to the listener."""

from llm_voice.errors.listener_error import ListenerError


class FailedToUnderstandListenerError(ListenerError):
    """Exception raised when the listener fails to understand speech in the audio."""

    def __init__(self) -> None:
        """Create a new FailedToUnderstandListenerError instance."""
        super().__init__("Could not understand speech in the audio.")
