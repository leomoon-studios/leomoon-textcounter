"""`frame_change_post` handler that drives all enabled text counters."""

from __future__ import annotations

import bpy
from bpy.app.handlers import persistent

from ..core.update import update_text_object


@persistent
def on_frame_change(scene: bpy.types.Scene, depsgraph: bpy.types.Depsgraph | None = None) -> None:
    if depsgraph is None:
        depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated_scene = scene.evaluated_get(depsgraph)
    for inst in depsgraph.object_instances:
        obj = inst.object
        if obj.type != "FONT":
            continue
        props = getattr(obj.data, "text_counter_props", None)
        if props is None or not props.if_animated:
            continue
        update_text_object(obj, evaluated_scene, depsgraph)


def _remove_existing() -> None:
    """Remove any previously-registered instance (matched by name)."""
    handlers = bpy.app.handlers.frame_change_post
    for h in list(handlers):
        if getattr(h, "__name__", "") == on_frame_change.__name__:
            handlers.remove(h)


def register() -> None:
    _remove_existing()
    bpy.app.handlers.frame_change_post.append(on_frame_change)


def unregister() -> None:
    _remove_existing()
