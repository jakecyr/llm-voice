"""No input listener error definition."""

from llm_voice.errors.listener_error import ListenerError


class NoInputListenerError(ListenerError):
    """Error raised when no speech is detected in the audio."""

    def __init__(self) -> None:
        """Create a new NoInputListenerError instance."""
        super().__init__("No speech detected in audio")
