"""Define an error class for when an invalid log level was referenced."""


class InvalidLogLevelError(Exception):
    """Invalid log level error when the provided log level is invalid."""

    def __init__(self, invalid_level_str: str) -> None:
        """Create a new InvalidLogLevelError instance."""
        super().__init__(f"{invalid_level_str} is not a valid logging level.")
