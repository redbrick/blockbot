from __future__ import annotations

import logging
import typing

import arc

if typing.TYPE_CHECKING:
    from src.config import Feature

logger = logging.getLogger(__name__)

type BlockbotContext = arc.Context[Blockbot]


class Blockbot(arc.GatewayClient):
    def add_plugin(self, plugin: BlockbotPlugin) -> typing.Self:  # pyright: ignore[reportIncompatibleMethodOverride]
        plugin_enabled: bool = True

        for feature in plugin.required_features:
            if not feature.enabled:
                plugin_enabled = False
                break

        if plugin_enabled:
            super().add_plugin(plugin)  # pyright: ignore[reportArgumentType]

        logger.debug(
            f"plugin '{plugin.name}' is {'enabled' if plugin_enabled else 'disabled'}"
        )

        return self


class BlockbotPlugin(arc.GatewayPluginBase[Blockbot]):
    def __init__(
        self, name: str, required_features: typing.Sequence[Feature] | None = None
    ) -> None:
        self._required_features = required_features or []
        super().__init__(name)

    @property
    def required_features(self) -> typing.Sequence[Feature]:
        """The features required for this plugin to be enabled."""
        return self._required_features
