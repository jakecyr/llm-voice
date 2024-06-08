"""Define the Spotify Client class."""

from __future__ import annotations

import os
from typing import Any

import spotipy

from llm_voice.utils.logger import logger


class SpotifyClient:
    """Spotify Client Class to Interact with Spotify APIs."""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str) -> None:
        """Create a Spotify client class."""
        self._client_id: str = client_id
        self._client_secret: str = client_secret
        self._redirect_uri: str = redirect_uri
        self._client: spotipy.Spotify | None = None

    def authorize(self) -> None:
        """Authorize the client."""
        scope = "user-read-playback-state,user-modify-playback-state"
        oauth_object = spotipy.SpotifyOAuth(
            self._client_id,
            self._client_secret,
            self._redirect_uri,
            scope=scope,
        )
        token_dict: Any = oauth_object.get_access_token()
        self._client = spotipy.Spotify(auth=token_dict["access_token"])

    def get_user(self) -> Any:
        """Get the user."""
        if self._client is None:
            raise ValueError("Client not initialized.")

        user: Any | None = self._client.current_user()
        return user

    def search(
        self,
        search_query: str,
        *,
        limit=1,
        offset=0,
        scope="playlist,artist,track,album,episode",
    ) -> list[dict]:
        """Search Spotify for songs, artists, playlists, albums, or episodes."""
        if self._client is None:
            raise ValueError("Client not initialized.")

        results: Any = self._client.search(
            search_query,
            limit=limit,
            offset=offset,
            type=scope,
        )

        scopes: list[str] = scope.split(",")
        combined_results: list[dict] = []

        for scope in scopes:
            combined_results.extend(results[scope + "s"]["items"])

        return combined_results

    def list_available_devices(self) -> list[dict]:
        """List all available devices to play on."""
        if self._client is None:
            raise ValueError("Client not initialized.")

        results: dict = self._client.devices()
        return results["devices"]

    def get_active_device(self) -> dict:
        """Get a current activate device."""
        if self._client is None:
            raise ValueError("Client not initialized.")

        devices: list[dict] = self.list_available_devices()

        for device in devices:
            if device["is_active"]:
                return device

        raise ValueError("No active device found.")

    def get_device_by_name(self, device_name: str) -> dict:
        """Get a device by name."""
        if self._client is None:
            raise ValueError("Client not initialized.")

        devices: list[dict] = self.list_available_devices()

        for device in devices:
            if device_name.lower() in device["name"].lower():
                return device

        raise ValueError(f"Device {device_name} not found.")

    def start_playback(
        self,
        device_id: str,
        *,
        uris: list[str] | None = None,
        context_uri: str | None = None,
    ) -> dict:
        """Start playback of the item on a selected device."""
        if self._client is None:
            raise ValueError("Client not initialized.")

        if not uris and not context_uri:
            raise ValueError("Expected either uris or context_uri to be defined.")

        results: Any = self._client.start_playback(
            device_id=device_id,
            uris=uris,
            context_uri=context_uri,
        )
        return results  # type: ignore

    def stop_playback(self, device_id: str) -> None:
        """Stop playback on the selected device.

        Args:
            device_id: ID of the device to stop playback on.
        """
        if self._client is None:
            raise ValueError("Client not initialized.")

        self._client.pause_playback(
            device_id=device_id,
        )


if __name__ == "__main__":
    """Execute the main functionality of the program."""
    from dotenv import load_dotenv

    load_dotenv()

    client = SpotifyClient(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    )

    client.authorize()
    song: dict = client.search("top hits", scope="playlist")[0]
    device: dict = client.get_active_device()

    logger.info(f"Starting track {song['type']} on {device['name']}...")

    if song["type"] == "track":
        client.start_playback(
            device_id=device["id"],
            uris=[f"spotify:track:{song['id']}"],
        )
    else:
        client.start_playback(
            device_id=device["id"],
            context_uri=f"spotify:{song['type']}:{song['id']}",
        )
