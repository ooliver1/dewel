# SPDX-License-Identifier: MIT

from logging import getLogger
from os import environ as env
from typing import Any

from aiohttp import ClientSession
from piston_rspy import Client
from velum import GatewayClient

log = getLogger(__name__)


class Dewel(GatewayClient):
    BASE_URL = "http://piston:2000/api/v2/"

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(
            cdn_url=env["CDN_URL"],
            gateway_url=env["GW_URL"],
            rest_url=env["REST_URL"],
            *args,
            **kwargs,
        )

        self.piston_client = Client.with_url(self.BASE_URL)

    async def start(self) -> None:
        await self.install_packages()
        return await super().start()

    async def install_packages(self) -> None:
        log.info("Installing packages...")

        async with ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/packages") as resp:
                packages: list = await resp.json()

            for package in packages:
                if not package["installed"]:
                    async with session.post(
                        f"{self.BASE_URL}/packages",
                        json={
                            "language": package["language"],
                            "version": package["language_version"],
                        },
                    ):
                        log.info(
                            f"Installed {package['language']}"
                            f"{package['language_version']}"
                        )
