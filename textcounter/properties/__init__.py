"""Property registration for the TextCounter add-on."""

from . import counter_props


def register() -> None:
    counter_props.register()


def unregister() -> None:
    counter_props.unregister()
