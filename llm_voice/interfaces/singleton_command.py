"""Define a base class for commands the assistant can handle."""

from abc import abstractmethod


class SingletonCommand:
    """Base class for commands the assistant can handle."""

    name: str
    description: str

    @abstractmethod
    def initialize(self) -> None:
        """Is called once on assistant startup."""

    @abstractmethod
    def execute(self, **kwargs) -> str | None:
        """Execute the command.

        Args:
            kwargs: Dynamic arguments passed to the command.

        Returns:
            The response string or None if no response is received.
        """

    @abstractmethod
    def to_json_schema(self) -> dict:
        """Convert the class to a JSON schema representation.

        Returns
            The JSON schema representation of the class.
        """
