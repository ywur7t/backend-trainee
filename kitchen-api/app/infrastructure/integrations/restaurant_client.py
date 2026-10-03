from typing import Any

import httpx


class RestaurantClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def get_restaurant(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/restaurant",
            )

        response.raise_for_status()

        return response.json()

    async def get_menu(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/menu",
            )

        response.raise_for_status()

        return response.json()