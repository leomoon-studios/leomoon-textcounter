# Stopwatch MM:SS — counter is total seconds, modulo 60 (e.g. 02:35)
import bpy

props = bpy.context.object.data.text_counter_props

props.mode = 'ANIMATED'
props.formatting = 'TIME'
props.time_separators = 1
props.time_modulo = 60
props.time_lead_zeroes = 2
props.time_trail_zeroes = 2
props.prefix = ''
props.suffix = ''
props.text_source_numeric = False
