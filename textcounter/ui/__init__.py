"""UI registration for the TextCounter add-on."""

from . import panel_counter


def register() -> None:
    panel_counter.register()


def unregister() -> None:
    panel_counter.unregister()
