"""Define the listener abstract interface."""

from abc import ABC, abstractmethod


class Listener(ABC):
    """Listener abstract interface."""

    @abstractmethod
    def listen(self) -> str:
        """Listen for user input and return the text.

        Returns
            The text from the speech listened to.
        """
