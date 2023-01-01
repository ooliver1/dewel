# SPDX-License-Identifier: MIT

from logging import getLogger
from typing import Any

from aiohttp import ClientSession
from piston_rspy import Client
from velum import GatewayClient

log = getLogger(__name__)


class Dewel(GatewayClient):
    BASE_URL = "http://piston:2000/api/v2/"

    def __init__(
        self,
        cdn_url: str | None = None,
        gateway_url: str | None = None,
        rest_url: str | None = None,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(cdn_url, gateway_url, rest_url, *args, **kwargs)

        self.piston_client = Client.with_url(self.BASE_URL)

    async def start(self) -> None:
        await self.install_packages()
        return await super().start()

    async def install_packages(self) -> None:
        log.info("Installing packages...")

        async with ClientSession() as session:
            # TODO: when I have my own list
            # async with session.get(f"{self.BASE_URL}/packages") as resp:
            #     packages: list = await resp.json()

            # for package in packages:
            #     if not package["installed"]:
            #         async with session.post(
            #             f"{self.BASE_URL}/packages",
            #             json={
            #                 "language": package["language"],
            #                 "version": package["language_version"],
            #             },
            #         ):
            #             log.info(f"Installed {package['language']}")

            async with session.post(
                f"{self.BASE_URL}/packages",
                json={
                    "language": "python",
                    "version": "3.10",
                },
            ):
                log.info("Installed python")
