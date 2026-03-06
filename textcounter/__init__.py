"""LeoMoon TextCounter — Blender 5.1+ extension."""

from . import handlers, operators, properties, ui
from .core.log import log


def register() -> None:
    properties.register()
    operators.register()
    ui.register()
    handlers.register()
    log("extension loaded")


def unregister() -> None:
    handlers.unregister()
    ui.unregister()
    operators.unregister()
    properties.unregister()
    log("extension unloaded")
