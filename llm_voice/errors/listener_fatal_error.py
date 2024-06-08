"""Define error when the listener fails."""

from llm_voice.errors.listener_error import ListenerError


class ListenerFatalError(ListenerError):
    """Generic error when trying to detect speech in audio."""

    def __init__(self) -> None:
        """Create a new ListenerFatalError instance."""
        super().__init__(
            "Error requesting results from Google Speech Recognition service",
        )
