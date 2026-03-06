"""Update pipeline: read property group, format the value, write to text body."""

from __future__ import annotations

from typing import Any

import bpy

from .expr_eval import evaluate
from .format_number import format_number
from .format_time import format_time


def _resolve_text_source_line(props: Any, counter: float) -> tuple[str, bool]:
    """Look up the line for the current counter value in the chosen Text block.

    Returns ``(line, is_numeric)``. ``is_numeric`` is True only when the user
    asked for `text_source_numeric` and the line successfully parsed as float.
    The numeric value (when applicable) is returned via the float conversion
    in `update_text_object`; here we just return the raw line.
    """
    txt = bpy.data.texts.get(props.text_source)
    if txt is None or not txt.lines:
        return "", False
    idx = max(0, min(int(counter), len(txt.lines) - 1))
    line = txt.lines[idx].body
    if props.text_source_numeric:
        try:
            float(line)
            return line, True
        except ValueError:
            return line, False
    return line, False


def _format_numeric(props: Any, value: float) -> str:
    if props.formatting == "NUMBER":
        return format_number(
            value,
            decimals=props.decimals,
            padding=props.padding,
            use_decimal=props.use_decimal,
            digit_sep=props.digit_separator,
            decimal_sep=props.decimal_separator,
            use_grouping=props.use_grouping,
            use_abbreviation=props.use_abbreviation,
            abbreviation_lower=props.abbreviation_lower,
            prefix=props.prefix,
            suffix=props.suffix,
        )
    return format_time(
        value,
        separators=props.time_separators,
        modulo=props.time_modulo,
        lead_zeroes=props.time_lead_zeroes,
        trail_zeroes=props.time_trail_zeroes,
        prefix=props.prefix,
        suffix=props.suffix,
    )


def update_text_object(text_obj: Any, scene: Any, depsgraph: Any) -> None:
    """Compute the displayed string for `text_obj` and write it to the body.

    `text_obj` is normally an evaluated object instance; we always write to
    its `.original.data.body` so the result persists in the source datablock.
    """
    data = text_obj.data
    props = getattr(data, "text_counter_props", None)
    if props is None or not props.if_animated:
        return

    # 1. Source value
    if props.mode == "ANIMATED":
        value = float(props.counter)
        # Clear result in ANIMATED mode
        if text_obj.original.data.text_counter_props.expression_result:
            text_obj.original.data.text_counter_props.expression_result = ""
    else:  # DYNAMIC
        value, err = evaluate(
            props.expression, scene=scene, depsgraph=depsgraph
        )
        # Write back via .original so it survives the depsgraph copy.
        if text_obj.original.data.text_counter_props.last_error != err:
            text_obj.original.data.text_counter_props.last_error = err
        # Store the evaluated result (as string)
        try:
            result_str = str(value)
        except Exception:
            result_str = ""
        if text_obj.original.data.text_counter_props.expression_result != result_str:
            text_obj.original.data.text_counter_props.expression_result = result_str

    # 2. Text-file override
    if props.use_text_source and props.text_source:
        line, is_numeric = _resolve_text_source_line(props, value)
        if is_numeric:
            try:
                value = float(line)
                out = _format_numeric(props, value)
            except ValueError:
                out = line
        else:
            # Raw text passthrough; still respect prefix/suffix.
            out = f"{props.prefix}{line}{props.suffix}"
    else:
        out = _format_numeric(props, value)

    # 3. Write to the original datablock so the change survives.
    text_obj.original.data.body = out
