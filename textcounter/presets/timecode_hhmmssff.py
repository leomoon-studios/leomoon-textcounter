# SMPTE-style timecode HH:MM:SS:FF — counter is frames, modulo 24 fps (e.g. 01:23:45:12)
import bpy

props = bpy.context.object.data.text_counter_props

props.mode = 'ANIMATED'
props.formatting = 'TIME'
props.time_separators = 3
props.time_modulo = 24
props.time_lead_zeroes = 2
props.time_trail_zeroes = 2
props.prefix = ''
props.suffix = ''
props.text_source_numeric = False
