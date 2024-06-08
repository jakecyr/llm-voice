"""Responder abstract object definition."""

from abc import ABC, abstractmethod


class Responder(ABC):
    """Abstract class for way to respond to user input."""

    @abstractmethod
    def generate(self, text_to_speak: str) -> None:
        """Respond to a request.

        Args:
            text_to_speak: The incoming request to respond to.

        Returns:
            The response.
        """
