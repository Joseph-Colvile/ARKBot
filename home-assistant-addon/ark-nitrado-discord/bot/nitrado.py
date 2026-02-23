from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


class NitradoApiError(RuntimeError):
    pass


@dataclass(slots=True)
class ServerStatus:
    state: str
    query_status: str | None
    player_current: int | None
    player_max: int | None
    game_human: str | None

    @property
    def is_online(self) -> bool:
        value = (self.state or "").lower()
        return value in {"started", "starting", "running"}


class NitradoClient:
    def __init__(self, token: str, service_id: str, timeout: float = 20.0) -> None:
        self.service_id = service_id
        self.base_url = "https://api.nitrado.net"
        self.http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Authorization": f"Bearer {token}"},
        )

    async def close(self) -> None:
        await self.http.aclose()

    async def _get_json(self, path: str) -> dict[str, Any]:
        response = await self.http.get(path)
        if response.status_code >= 400:
            raise NitradoApiError(
                f"Nitrado request failed ({response.status_code}): {response.text[:300]}"
            )
        return response.json()

    async def _post_json(self, path: str) -> dict[str, Any]:
        response = await self.http.post(path)
        if response.status_code >= 400:
            raise NitradoApiError(
                f"Nitrado request failed ({response.status_code}): {response.text[:300]}"
            )
        return response.json()

    async def get_status(self) -> ServerStatus:
        payload = await self._get_json(f"/services/{self.service_id}/gameservers")
        data = payload.get("data", {})
        gs = data.get("gameserver", {})
        settings = gs.get("settings", {})
        query = gs.get("query", {})

        players = query.get("player_current")
        player_max = query.get("player_max")

        return ServerStatus(
            state=str(gs.get("status", "unknown")),
            query_status=query.get("status"),
            player_current=int(players) if isinstance(players, int | str) and str(players).isdigit() else None,
            player_max=int(player_max) if isinstance(player_max, int | str) and str(player_max).isdigit() else None,
            game_human=settings.get("config", {}).get("game_human"),
        )

    async def power_on(self) -> str:
        payload = await self._post_json(f"/services/{self.service_id}/gameservers/start")
        message = payload.get("message") or "Start command sent."
        return str(message)

    async def power_off(self) -> str:
        payload = await self._post_json(f"/services/{self.service_id}/gameservers/stop")
        message = payload.get("message") or "Stop command sent."
        return str(message)
