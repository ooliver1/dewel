# SPDX-License-Identifier: MIT

from logging import getLogger
from os import environ as env
from typing import Any

from aiohttp import ClientSession
from velum import GatewayClient
from yarl import URL

log = getLogger(__name__)


class Dewel(GatewayClient):
    BASE_URL = URL(f"{env['PISTON_URL']}/api/v2/")

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

        self.piston_client: ClientSession = None  # type: ignore

    async def start(self) -> None:
        self.piston_client = ClientSession()
        await self.install_packages()
        return await super().start()

    async def close(self) -> None:
        await self.piston_client.close()
        return await super().close()

    async def install_packages(self) -> None:
        log.info("Installing packages...")

        async with self.piston_client.get(self.BASE_URL / "packages") as resp:
            packages: list = await resp.json()

        for package in packages:
            if not package["installed"]:
                async with self.piston_client.post(
                    self.BASE_URL / "packages",
                    json={
                        "language": package["language"],
                        "version": package["language_version"],
                    },
                ):
                    log.info(
                        f"Installed {package['language']}"
                        f"{package['language_version']}"
                    )
