"""Properties-editor panels for the TextCounter add-on."""

from __future__ import annotations

import bpy
from bpy.types import Context, Panel


class OBJECT_PT_textcounter(Panel):
    bl_label = "LeoMoon TextCounter"
    bl_idname = "OBJECT_PT_textcounter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context: Context) -> bool:
        obj = context.object
        return obj is not None and obj.type == "FONT"

    def draw_header(self, context: Context) -> None:
        props = context.object.data.text_counter_props
        self.layout.prop(props, "if_animated", text="")

    def draw(self, context: Context) -> None:
        layout = self.layout
        props = context.object.data.text_counter_props

        # --- Header row: presets + copy/paste + bake (always enabled) ---
        tools = layout.row(align=True)
        tools.menu("TEXTCOUNTER_MT_presets", text="New Preset")
        tools.operator("textcounter.preset_add", text="", icon="ADD")
        tools.operator(
            "textcounter.preset_add", text="", icon="REMOVE"
        ).remove_active = True
        tools.separator()
        tools.operator("textcounter.copy_settings", text="", icon="COPYDOWN")
        tools.operator("textcounter.paste_settings", text="", icon="PASTEDOWN")

        # Everything else greys out when the master toggle is off.
        body = layout.column()
        body.enabled = props.if_animated

        # --- Mode --------------------------------------------------------
        row = body.row()
        row.prop(props, "mode", expand=True)

        row = body.row()
        if props.mode == "ANIMATED":
            row.prop(props, "counter")
        else:  # DYNAMIC
            row.prop(props, "expression", text="Expr")
            # Show evaluated result (read-only)
            res_row = body.row()
            res_row.enabled = False
            res_row.prop(props, "expression_result", text="Result")
            if props.last_error:
                err = body.row()
                err.alert = True
                err.label(text=props.last_error, icon="ERROR")

        # --- Formatting --------------------------------------------------
        box = body.box()
        col = box.column()
        row = col.row(align=True)
        row.prop(props, "formatting", expand=True)

        if props.formatting == "NUMBER":
            row = col.row(align=True)
            row.prop(props, "use_decimal", text="Decimal")
            row.prop(props, "padding")
            sub = row.row(align=True)
            sub.enabled = props.use_decimal
            sub.prop(props, "decimals")

            row = col.row(align=True)
            row.prop(props, "prefix")
            row.prop(props, "suffix")

            row = col.row(align=True)
            row.prop(props, "use_grouping", text="Digit Grouping")

            row = col.row(align=True)
            row.prop(props, "use_abbreviation", text="Abbreviate")
            sub = row.row(align=True)
            sub.enabled = props.use_abbreviation
            sub.prop(props, "abbreviation_lower", text="Lowercase")

            # Separator box
            sep_box = body.box()
            split = sep_box.split()
            c1 = split.column()
            c1.enabled = props.use_decimal
            c1.prop(props, "decimal_separator", text="Decimal sep.")
            c2 = split.column()
            c2.enabled = props.use_grouping
            c2.prop(props, "digit_separator", text="Digit sep.")

        else:  # TIME
            row = col.row(align=False)
            row.prop(props, "time_separators")
            row.prop(props, "time_modulo")
            row = col.row(align=True)
            row.prop(props, "time_lead_zeroes")
            row.prop(props, "time_trail_zeroes")
            row = col.row(align=True)
            row.prop(props, "prefix")
            row.prop(props, "suffix")


class OBJECT_PT_textcounter_source(Panel):
    bl_label = "Text File Source"
    bl_idname = "OBJECT_PT_textcounter_source"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_parent_id = "OBJECT_PT_textcounter"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        obj = context.object
        return obj is not None and obj.type == "FONT"

    def draw_header(self, context: Context) -> None:
        props = context.object.data.text_counter_props
        self.layout.prop(props, "use_text_source", text="")

    def draw(self, context: Context) -> None:
        layout = self.layout
        props = context.object.data.text_counter_props
        layout.enabled = props.if_animated and props.use_text_source

        row = layout.row(align=True)
        row.prop(props, "text_source_numeric", text="Numerical Formatting")
        row.prop_search(props, "text_source", bpy.data, "texts", text="Text File")


_classes = (
    OBJECT_PT_textcounter,
    OBJECT_PT_textcounter_source,
)


def register() -> None:
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
