# Percentage — one decimal place with a trailing % sign (e.g. 42.5%)
import bpy

props = bpy.context.object.data.text_counter_props

props.mode = 'ANIMATED'
props.formatting = 'NUMBER'
props.use_decimal = True
props.decimals = 1
props.padding = 1
props.use_grouping = False
props.digit_separator = ','
props.decimal_separator = '.'
props.use_abbreviation = False
props.abbreviation_lower = False
props.prefix = ''
props.suffix = '%'
props.text_source_numeric = False
