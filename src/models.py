from __future__ import annotations

import importlib
import logging
import pathlib
import sys
import typing

import arc
from arc import ExtensionLoadError

if typing.TYPE_CHECKING:
    from arc.abc import CallableCommandBase
    from arc.internal.types import BuilderT

    from src.config import Feature

logger = logging.getLogger(__name__)

type BlockbotContext = arc.Context[Blockbot]


def command_loader(
    callback: typing.Callable[[BlockbotPlugin], None] | None = None,
) -> (
    typing.Callable[[BlockbotPlugin], None]
    | typing.Callable[
        [typing.Callable[[BlockbotPlugin], None]],
        typing.Callable[[BlockbotPlugin], None],
    ]
):
    def decorator(
        func: typing.Callable[[BlockbotPlugin], None],
    ) -> typing.Callable[[BlockbotPlugin], None]:
        module = sys.modules[func.__module__]
        setattr(module, "__arc_extension_loader__", func)
        return func

    if callback is not None:
        return decorator(callback)

    return decorator


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

    def load_commands_from(
        self, dir_path: str | pathlib.Path, recursive: bool = False
    ) -> typing.Self:
        if isinstance(dir_path, str):
            dir_path = pathlib.Path(dir_path)

        try:
            dir_path.absolute().relative_to(pathlib.Path.cwd())
        except ValueError:
            raise ExtensionLoadError(
                "dir_path must be relative to the current working directory."
            )

        if not dir_path.is_dir():
            raise ExtensionLoadError("dir_path must exist and be a directory.")

        globfunc = dir_path.rglob if recursive else dir_path.glob
        loaded = 0

        for file in globfunc(r"**/[!_]*.py"):
            module_path = ".".join(file.as_posix()[:-3].split("/"))
            self.load_command(module_path)
            loaded += 1

        if loaded == 0:
            logger.warning(f"No extensions were found at '{dir_path}'.")

        return self

    def load_command(self, path: str) -> typing.Self:
        parents = path.split(".")
        name = parents.pop()

        pkg = ".".join(parents)

        if pkg:
            name = "." + name

        module = importlib.import_module(path, package=pkg)

        loader = getattr(module, "__arc_extension_loader__", None)

        if loader is None:
            raise ValueError(f"Module '{path}' does not have a loader.")
        loader(self)
        logger.info(f"Loaded command: '{path}' for plugin '{self.name}'.")

        return self

    def add_command(self, command: CallableCommandBase[Blockbot, BuilderT]) -> None:
        self.include(command)
