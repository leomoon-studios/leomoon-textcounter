# Padded score — 6-digit zero-padded integer (e.g. 001234)
import bpy

props = bpy.context.object.data.text_counter_props

props.mode = 'ANIMATED'
props.formatting = 'NUMBER'
props.use_decimal = False
props.decimals = 0
props.padding = 6
props.use_grouping = False
props.digit_separator = ','
props.decimal_separator = '.'
props.use_abbreviation = False
props.abbreviation_lower = False
props.prefix = ''
props.suffix = ''
props.text_source_numeric = False
