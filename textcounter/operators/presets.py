"""TextCounter preset operator and menu.

Uses Blender's standard `AddPresetBase` flow so presets are stored under
`<scripts>/presets/textcounter/` and listed in a header menu in the panel.
On register, any preset shipped under `textcounter/presets/textcounter/`
inside the extension is copied into the user presets folder if missing,
so users see a curated set of starting points without overwriting their
own saved presets.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import bpy
from bl_operators.presets import AddPresetBase
from bpy.types import Menu, Operator

from ..core.log import log

PRESET_SUBDIR = "textcounter"

# Properties that get serialized into the .py preset file.
_PRESET_PROPS = [
    "props.mode",
    "props.expression",
    "props.formatting",
    "props.use_decimal",
    "props.decimals",
    "props.padding",
    "props.use_grouping",
    "props.digit_separator",
    "props.decimal_separator",
    "props.use_abbreviation",
    "props.abbreviation_lower",
    "props.time_separators",
    "props.time_modulo",
    "props.time_lead_zeroes",
    "props.time_trail_zeroes",
    "props.prefix",
    "props.suffix",
    "props.text_source_numeric",
]


class TEXTCOUNTER_MT_presets(Menu):
    bl_label = "TextCounter Presets"
    preset_subdir = PRESET_SUBDIR
    preset_operator = "script.execute_preset"

    # Special-cased capitalisation overrides for known preset stems. Stems
    # not listed fall back to a Title Case conversion of the filename.
    _LABEL_OVERRIDES = {
        "currency_usd": "Currency USD",
        "currency_eur": "Currency EUR",
        "stopwatch_mmss": "Stopwatch MM:SS",
        "timecode_hhmmssff": "Timecode HH:MM:SS:FF",
    }

    @classmethod
    def _label_for(cls, filename: str) -> str:
        stem = Path(filename).stem
        if stem in cls._LABEL_OVERRIDES:
            return cls._LABEL_OVERRIDES[stem]
        return stem.replace("_", " ").title()

    @classmethod
    def active_label(cls, context) -> str:
        """Pretty label of the currently selected preset, or the menu label."""
        active = getattr(context.window_manager, "preset_name", "") or ""
        if active:
            return cls._label_for(active)
        return cls.bl_label

    def draw(self, context):
        layout = self.layout
        paths = bpy.utils.preset_paths(self.preset_subdir)
        entries = []
        for base in paths:
            base_path = Path(base)
            if not base_path.is_dir():
                continue
            for f in sorted(base_path.glob("*.py")):
                entries.append((self._label_for(f.name), str(f)))
        entries.sort(key=lambda e: e[0].lower())
        for label, filepath in entries:
            op = layout.operator(self.preset_operator, text=label)
            op.filepath = filepath
            op.menu_idname = self.bl_idname


class TEXTCOUNTER_OT_add_preset(AddPresetBase, Operator):
    """Add or remove a TextCounter preset"""

    bl_idname = "textcounter.preset_add"
    bl_label = "Add TextCounter Preset"
    preset_menu = "TEXTCOUNTER_MT_presets"
    preset_subdir = PRESET_SUBDIR

    preset_defines = [
        "props = bpy.context.object.data.text_counter_props",
    ]
    preset_values = _PRESET_PROPS


_classes = (
    TEXTCOUNTER_MT_presets,
    TEXTCOUNTER_OT_add_preset,
)


def _bundled_preset_dir() -> Path:
    """Return the bundled `presets/` folder shipped with the extension."""
    return Path(__file__).resolve().parent.parent / "presets"


def _user_preset_dir() -> Path:
    return Path(
        bpy.utils.user_resource("SCRIPTS", path=f"presets/{PRESET_SUBDIR}", create=True)
    )


def _install_bundled_presets() -> None:
    """Copy any bundled presets that the user does not already have."""
    src = _bundled_preset_dir()
    if not src.is_dir():
        return
    dst = _user_preset_dir()
    for preset in src.glob("*.py"):
        target = dst / preset.name
        if not target.exists():
            try:
                shutil.copyfile(preset, target)
            except OSError as exc:
                log(f"failed to install preset {preset.name}: {exc}")


def register() -> None:
    for cls in _classes:
        bpy.utils.register_class(cls)
    _install_bundled_presets()


def unregister() -> None:
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
