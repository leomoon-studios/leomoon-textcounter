"""Copy/paste TextCounter settings between text objects."""

from __future__ import annotations

import bpy
from bpy.types import Operator

# Module-level clipboard for property-group fields (key -> value).
_CLIPBOARD: dict[str, object] = {}

# Fields to skip when copying — runtime/error state, not user config.
_SKIP_FIELDS = frozenset({"last_error"})


def _iter_prop_keys(props) -> list[str]:
    return [k for k in props.bl_rna.properties if k != "rna_type" and k not in _SKIP_FIELDS]


class TEXTCOUNTER_OT_copy_settings(Operator):
    """Copy this Text object's TextCounter settings to the internal clipboard"""

    bl_idname = "textcounter.copy_settings"
    bl_label = "Copy TextCounter Settings"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context) -> bool:
        obj = context.object
        return obj is not None and obj.type == "FONT"

    def execute(self, context):
        global _CLIPBOARD
        props = context.object.data.text_counter_props
        _CLIPBOARD = {key: getattr(props, key) for key in _iter_prop_keys(props)}
        self.report({"INFO"}, f"Copied {len(_CLIPBOARD)} TextCounter settings")
        return {"FINISHED"}


class TEXTCOUNTER_OT_paste_settings(Operator):
    """Paste TextCounter settings onto the selected Text object(s)"""

    bl_idname = "textcounter.paste_settings"
    bl_label = "Paste TextCounter Settings"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context) -> bool:
        if not _CLIPBOARD:
            return False
        obj = context.object
        return obj is not None and obj.type == "FONT"

    def execute(self, context):
        targets = [
            o for o in context.selected_objects if o.type == "FONT"
        ] or [context.object]

        applied = 0
        for obj in targets:
            props = obj.data.text_counter_props
            for key, value in _CLIPBOARD.items():
                try:
                    setattr(props, key, value)
                except (AttributeError, TypeError):
                    # Property may have been removed in a future version.
                    continue
            applied += 1

        self.report({"INFO"}, f"Pasted TextCounter settings to {applied} object(s)")
        return {"FINISHED"}


_classes = (
    TEXTCOUNTER_OT_copy_settings,
    TEXTCOUNTER_OT_paste_settings,
)


def register() -> None:
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
