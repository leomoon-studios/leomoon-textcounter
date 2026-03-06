"""Property group for the TextCounter add-on.

Defines `TextCounterProps`, attached to `bpy.types.TextCurve` as
`text_counter_props`. All formatting/data fields used by the add-on live here.
"""

from __future__ import annotations

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)
from bpy.types import Context, PropertyGroup, TextCurve


def _on_prop_update(self: TextCounterProps, context: Context) -> None:
    """Shared update callback.

    Tags the owning text object for redraw and immediately recomputes the
    displayed body so users see changes without scrubbing the timeline.
    """
    obj = getattr(context, "object", None)
    if obj is None or obj.type != "FONT":
        return
    obj.update_tag(refresh={"DATA"})

    # Lazy import to avoid a circular import at module load time.
    from ..core.log import log
    from ..core.update import update_text_object

    scene = context.scene
    depsgraph = context.evaluated_depsgraph_get() if context else None
    try:
        update_text_object(obj, scene, depsgraph)
    except Exception as exc:  # pragma: no cover - defensive
        log(f"live update failed: {exc}")


_MODE_ITEMS = [
    ("ANIMATED", "Animated", "Counter values from f-curves"),
    ("DYNAMIC", "Dynamic", "Counter values from a Python expression"),
]

_FORMATTING_ITEMS = [
    ("NUMBER", "Number", "Display the counter as a number"),
    ("TIME", "Time", "Display the counter as a time string"),
]

_DIGIT_SEP_ITEMS = [
    (",", ", (Comma)", ","),
    (".", ". (Dot)", "."),
    (" ", "  (Space)", " "),
    ("'", "' (Apostrophe)", "'"),
]

_DECIMAL_SEP_ITEMS = [
    (",", ", (Comma)", ","),
    (".", ". (Dot)", "."),
]


class TextCounterProps(PropertyGroup):
    """Per-text counter configuration."""

    # --- master toggle & source mode ------------------------------------
    if_animated: BoolProperty(
        name="Counter Active",
        description="Enable the counter for this text object",
        default=False,
        update=_on_prop_update,
    )
    mode: EnumProperty(
        name="Mode",
        description="How the counter value is produced",
        items=_MODE_ITEMS,
        default="ANIMATED",
        update=_on_prop_update,
    )
    counter: FloatProperty(
        name="Counter",
        description="Animated counter value (keyframe this)",
        default=0.0,
        update=_on_prop_update,
    )
    expression: StringProperty(
        name="Expression",
        description="Python expression evaluated each frame to produce the counter value",
        default="",
        update=_on_prop_update,
    )
    last_error: StringProperty(
        name="Last Error",
        description="Most recent expression evaluation error (empty = no error)",
        default="",
    )
    expression_result: StringProperty(
        name="Evaluated Result",
        description="Result of evaluating the expression (read-only)",
        default="",
        options={'SKIP_SAVE'},
    )

    # --- formatting selector --------------------------------------------
    formatting: EnumProperty(
        name="Formatting",
        description="How to format the counter value",
        items=_FORMATTING_ITEMS,
        default="NUMBER",
        update=_on_prop_update,
    )

    # --- number formatting ----------------------------------------------
    use_decimal: BoolProperty(
        name="Decimal",
        description="Show fractional digits",
        default=False,
        update=_on_prop_update,
    )
    decimals: IntProperty(
        name="Decimals",
        description="Number of fractional digits to show",
        default=2,
        min=0,
        soft_max=12,
        update=_on_prop_update,
    )
    padding: IntProperty(
        name="Padding",
        description="Minimum number of integer digits (zero-padded)",
        default=1,
        min=1,
        soft_max=20,
        update=_on_prop_update,
    )
    use_grouping: BoolProperty(
        name="Digit Grouping",
        description="Group large numbers with a separator",
        default=False,
        update=_on_prop_update,
    )
    digit_separator: EnumProperty(
        name="Digit Separator",
        description="Separator used for digit grouping",
        items=_DIGIT_SEP_ITEMS,
        default=",",
        update=_on_prop_update,
    )
    decimal_separator: EnumProperty(
        name="Decimal Separator",
        description="Character used between integer and fractional parts",
        items=_DECIMAL_SEP_ITEMS,
        default=".",
        update=_on_prop_update,
    )
    use_abbreviation: BoolProperty(
        name="Abbreviate",
        description="Abbreviate large numbers (K, M, B, T, Q)",
        default=False,
        update=_on_prop_update,
    )
    abbreviation_lower: BoolProperty(
        name="Lowercase Abbreviation",
        description="Use lowercase abbreviation suffixes",
        default=False,
        update=_on_prop_update,
    )

    # --- time formatting ------------------------------------------------
    time_separators: IntProperty(
        name="Separators",
        description="Number of ':' separators (0=SS, 1=MM:SS, 2=HH:MM:SS, 3=DD:HH:MM:SS)",
        default=0,
        min=0,
        max=3,
        update=_on_prop_update,
    )
    time_modulo: IntProperty(
        name="Last Separator Modulo",
        description="Modulo for the smallest unit (e.g. frame rate)",
        default=24,
        min=1,
        update=_on_prop_update,
    )
    time_lead_zeroes: IntProperty(
        name="Leading Zeroes",
        description="Width of the largest time field",
        default=2,
        min=1,
        update=_on_prop_update,
    )
    time_trail_zeroes: IntProperty(
        name="Trailing Zeroes",
        description="Width of the smallest time field",
        default=2,
        min=1,
        update=_on_prop_update,
    )

    # --- prefix / suffix ------------------------------------------------
    prefix: StringProperty(
        name="Prefix",
        description="Text shown before the counter",
        default="",
        update=_on_prop_update,
    )
    suffix: StringProperty(
        name="Suffix",
        description="Text shown after the counter",
        default="",
        update=_on_prop_update,
    )

    # --- text-file source ----------------------------------------------
    use_text_source: BoolProperty(
        name="Override with Text File",
        description="Use a Blender Text data-block as the line-indexed source",
        default=False,
        update=_on_prop_update,
    )
    text_source: StringProperty(
        name="Text File",
        description="Name of the Blender Text data-block to read lines from",
        default="",
        update=_on_prop_update,
    )
    text_source_numeric: BoolProperty(
        name="Numerical Formatting",
        description="Parse the selected line as a number and apply numeric formatting",
        default=False,
        update=_on_prop_update,
    )


_classes = (TextCounterProps,)


def register() -> None:
    for cls in _classes:
        bpy.utils.register_class(cls)
    TextCurve.text_counter_props = PointerProperty(type=TextCounterProps)


def unregister() -> None:
    if hasattr(TextCurve, "text_counter_props"):
        del TextCurve.text_counter_props
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
