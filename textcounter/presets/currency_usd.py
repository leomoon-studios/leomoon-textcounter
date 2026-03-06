# Currency — US dollars with thousands grouping and 2 decimals (e.g. $1,234.56)
import bpy

props = bpy.context.object.data.text_counter_props

props.mode = 'ANIMATED'
props.formatting = 'NUMBER'
props.use_decimal = True
props.decimals = 2
props.padding = 1
props.use_grouping = True
props.digit_separator = ','
props.decimal_separator = '.'
props.use_abbreviation = False
props.abbreviation_lower = False
props.prefix = '$'
props.suffix = ''
props.text_source_numeric = False
