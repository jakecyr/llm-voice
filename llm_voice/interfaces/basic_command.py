"""Define a base class for commands the assistant can handle."""

from abc import ABC, abstractmethod


class BasicCommand(ABC):
    """Base class for commands the assistant can handle."""

    name: str
    description: str

    @abstractmethod
    def execute(self) -> str | None:
        """Execute the command.

        Returns
            The response string or None if no response is received.
        """

    @classmethod
    def to_json_schema(cls) -> dict:
        """Convert the class to a JSON schema representation.

        Returns
            The JSON schema representation of the class.
        """
        raise NotImplementedError
