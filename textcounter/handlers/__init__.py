"""Handler registration for the TextCounter add-on."""

from . import frame_change


def register() -> None:
    frame_change.register()


def unregister() -> None:
    frame_change.unregister()
