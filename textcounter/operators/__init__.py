"""Operator registration for the TextCounter add-on."""

from . import copy_paste, presets


def register() -> None:
    copy_paste.register()
    presets.register()


def unregister() -> None:
    presets.unregister()
    copy_paste.unregister()
