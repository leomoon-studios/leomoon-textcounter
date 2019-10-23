bl_info = {
    "name": "LeoMoon TextCounter",
    "author": "LeoMoon Studios - www.LeoMoon.com and Marcin Zielinski - www.marcin-zielinski.tk/en/",
    "version": (1, 3, 2),
    "blender": (2, 80, 0),
    "location": "Font Object Data > LeoMoon TextCounter",
    "description": "Text counter for displays, HUDs etc.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Animation"}

import bpy
from bpy.props import FloatProperty, PointerProperty, BoolProperty, IntProperty, EnumProperty, StringProperty
from bpy.app.handlers import persistent
from math import log, ceil

abbreviations = ["","K","M","B","T","Q"]
millions = ["","thousand","million","billion","trillion","quadrillion"]

def isAPI28():
    return bpy.app.version >= (2, 80)

def make_annotations(cls):
    """Converts class fields to annotations if running with Blender 2.8"""
    if bpy.app.version < (2, 80):
        return cls
    bl_props = {k: v for k, v in cls.__dict__.items() if isinstance(v, tuple)}
    if bl_props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in bl_props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls

def formatCounter(input, timeSeparators, timeLeadZeroes, timeTrailZeroes, timeModulo):
    f=0
    s=0
    m=0
    h=0
    out=''
    neg=''
    if input < 0:
        neg = '-'
        input = abs(input)
        
    if timeSeparators >= 0:
        if timeSeparators == 0:
            out = int(input)
            out = format(out, '0'+str(timeLeadZeroes)+'d')
        else:
            s,f = divmod(int(input), timeModulo)
            out = format(f, '0'+str(timeLeadZeroes)+'d')
            
    if timeSeparators >= 1:
        if timeSeparators == 1:
            out = format(s, '0'+str(timeTrailZeroes)+'d')+":"+out
        else:
            m,s = divmod(s, 60)
            out = format(s, '02d')+":"+out

    if timeSeparators >= 2:
        if timeSeparators == 2:
            out = format(m, '0'+str(timeTrailZeroes)+'d')+":"+out
        else:
            h,m = divmod(m, 60)
            out = format(m, '02d')+":"+out

    if timeSeparators >= 3:
        out = format(h, '0'+str(timeTrailZeroes)+'d')+":"+out
        
    return neg + out

#
class TextCounter_Props(bpy.types.PropertyGroup):
    def val_up(self, context):
        textcounter_update_val(context.object, context.scene)
    ifAnimated = BoolProperty(name='Counter Active', default=False, update=val_up)
    counter = FloatProperty(name='Counter', update=val_up)
    padding = IntProperty(name='Padding', update=val_up, min=1)
    ifDecimal = BoolProperty(name='Decimal', default=False, update=val_up)
    decimals = IntProperty(name='Decimal', update=val_up, min=0, default=2)
    typeEnum = EnumProperty(items=[('ANIMATED', 'Animated', 'Counter values from f-curves'), ('DYNAMIC', 'Dynamic', 'Counter values from expression')], name='Type', update=val_up, default='ANIMATED')
    formattingEnum = EnumProperty(items=[('NUMBER', 'Number', 'Counter values as numbers'), ('TIME', 'Time', 'Counter values as time')], name='Formatting Type', update=val_up, default='NUMBER')
    expr = StringProperty(name='Expression', update=val_up, default='')
    prefix = StringProperty(name='Prefix', update=val_up, default='')
    sufix = StringProperty(name='Sufix', update=val_up, default='')
    ifTextFile = BoolProperty(name='Override with Text File', default=False, update=val_up)
    textFile = StringProperty(name='Text File', update=val_up, default='')
    ifTextFormatting = BoolProperty(name='Numerical Formatting', default=False, update=val_up)
    timeSeparators = IntProperty(name='Separators', update=val_up, min=0, max=3)
    timeModulo = IntProperty(name='Last Separator Modulo', update=val_up, min=1, default=24)
    timeLeadZeroes = IntProperty(name='Leading Zeroes', update=val_up, min=1, default=2)
    timeTrailZeroes = IntProperty(name='Trailing Zeroes', update=val_up, min=1, default=2)

    # newly added
    useDigitGrouping = BoolProperty(
        name='Digit Grouping', default=False, update=val_up,
        description='Use digint grouping in large numbers')
    useAbbreviation = BoolProperty(name='Abbreviate', default=False, update=val_up,
        description='Use large or small number abbreviations')
    useAbbreviationLower = BoolProperty(name='Lowercase', default=False, update=val_up,
        description='Use lowercase abbreviations')
    digitSeparator = EnumProperty(
        name="Digit grouping",
        description="Digit grouping separator",
        items=[
            (',', ', (Comma)', ','),
            ('.', '. (Dot)', '.'),
            (' ', ' (Space)', ' '),
            ("'", "' (Apostrophe)", "'"),
        ],
        default=',',
        update=val_up
    )
    decimalSeparator = EnumProperty(
        name="Decimal separator",
        description="Decimal separator",
        items=[
            (',', ', (Comma)', ','),
            ('.', '. (Dot)', '.'),
        ],
        default='.',
        update=val_up
    )

    def dyn_get(self):
        # shortcut vars to be used in expresion
        context = bpy.context
        C = context
        scene = C.scene
        try:
            return str(eval(self.expr))
        except Exception as e:
            print('Expr Error: '+str(e.args))
    dynamicCounter = StringProperty(name='Dynamic Counter', get=dyn_get, default='')
    
    def form_up(self, context):
        textcounter_update_val(context.object, context.scene)
    def form_get(self):
        input=0
        if self.typeEnum == 'ANIMATED':
            input = float(self.counter)
        elif self.typeEnum == 'DYNAMIC':
            input = float(self.dynamicCounter)
        return formatCounter(input, self.timeSeparators, self.timeLeadZeroes, self.timeTrailZeroes, self.timeModulo)

    def form_set(self, value):
        counter = 0
        separators = value.split(':')
        for idx, i in enumerate(separators[:-1]):
            counter += int(i) * 60**(len(separators)-2-idx)*self.timeModulo
        counter += int(separators[-1])
        self.counter = float(counter)
        

    formattedCounter = StringProperty(name='Formatted Counter', get=form_get, set=form_set, default='')
    

#
class TEXTCOUNTER1_PT_panel(bpy.types.Panel):
    """Creates a Panel in the Font properties window"""
    bl_label = "LeoMoon TextCounter"
    bl_idname = "TEXTCOUNTER1_PT_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    counter = FloatProperty(name='Counter')
    @classmethod
    def poll(cls, context):
        return context.object.type == 'FONT'

    def draw_header(self, context):
        self.layout.prop(context.object.data.text_counter_props, 'ifAnimated', text='')

    def draw(self, context):
        props = context.object.data.text_counter_props

        layout = self.layout
        layout.enabled = props.ifAnimated
        row = layout.row()
        row.prop(props, 'typeEnum', expand=True)
        row = layout.row()
        if props.typeEnum == 'ANIMATED':
            row.prop(props, 'counter')
        elif props.typeEnum == 'DYNAMIC':
            row.prop(props, 'expr')
            row = layout.row()
            row.prop(props, 'dynamicCounter')
    
        #formatting type enum
        boxy = layout.box() 
        split =  boxy.split(align=True)
        col = split.column()
        row = col.row(align=True)
        row.prop(props, 'formattingEnum', expand=True)
        if props.formattingEnum == 'NUMBER':
            row = col.row(align=True)
            row.prop(props, 'ifDecimal')
            row.prop(props, 'padding')
            row.prop(props, 'decimals')
            row = col.row(align=True)
            row.prop(props, 'prefix')
            row.prop(props, 'sufix')
            row = col.row(align=True)
            colsub = row.column()
            colsub.prop(props, 'useDigitGrouping')
            colsub = row.column()
            colsub.enabled = props.useDigitGrouping
            row = col.row(align=True)
            colsub = row.column()
            colsub.prop(props, 'useAbbreviation')
            colsub = row.column()
            colsub.enabled = props.useAbbreviation
            colsub.prop(props, 'useAbbreviationLower')

        elif props.formattingEnum == 'TIME':
            row = col.row(align=True)
            row.prop(props, 'formattedCounter')
            row = col.row(align=False)
            row.prop(props, 'timeSeparators')
            row.prop(props, 'timeModulo')
            row = col.row(align=True)
            row.prop(props, 'timeLeadZeroes')
            row.prop(props, 'timeTrailZeroes')
            row = col.row(align=True)
            row.prop(props, 'prefix')
            row.prop(props, 'sufix')
        
        if props.formattingEnum == "NUMBER":
            boxy = layout.box()
            split = boxy.split()
            col = split.column()
            col.enabled = True if props.ifDecimal else False
            col.prop(props, 'decimalSeparator')
            col = split.column()
            col.enabled = True if props.useDigitGrouping else False
            col.prop(props, 'digitSeparator')

        boxy = layout.box() 
        row = boxy.row()
        row.prop(props, 'ifTextFile')
        row = boxy.row()
        row.prop(props, "ifTextFormatting")
        row.prop_search(props, "textFile", bpy.data, "texts", text="Text File")
        if not props.ifTextFile:
            row.enabled = False
            
            
        

def textcounter_update_val(text, scene):
    def formatPaddingCommas(line):
        # left_len = len(str(int(line)))
        # left_len = ceil(log(abs(line))/log(10))
        padding = props.padding
        comas, comas_mod = divmod(padding, 3)
        if comas_mod == 0:
            # <0,>000
            comas -= 1
        if props.ifDecimal:
            # include decimal dot
            padding += 1
        padding = padding+props.decimals*props.ifDecimal
        padding += comas*props.useDigitGrouping
        return ('{0:0{pad}{comma}.{dec}f}').format(line,
                        dec=props.decimals*int(props.ifDecimal),
                        pad=padding,
                        comma=',' if props.useDigitGrouping else '').replace('.', '@').replace(',', props.digitSeparator).replace('@', props.decimalSeparator)


    text.update_tag(refresh={'DATA'})
    props = text.data.text_counter_props
    counter = 0
    line = ''
    out = ''
    neg=''

    if props.ifAnimated == False:
        return # don't modify if disabled
    
    if props.typeEnum == 'ANIMATED':
        counter = props.counter
    elif props.typeEnum == 'DYNAMIC':
        try:
            counter = eval(props.expr)
        except Exception as e:
            print('Expr Error: '+str(e.args))

    isNumeric=True #always true for counter not overrided
    if props.ifTextFile:
        txt = bpy.data.texts[props.textFile]
        clampedCounter = max(0, min(int(counter), len(txt.lines)-1))
        line = txt.lines[clampedCounter].body        
        if props.ifTextFormatting:
            try:
                line = float(line)
            except Exception:
                isNumeric = False
                out = line
        else:
            isNumeric = False
            out = line
    else:
        line = counter

    if isNumeric:  
        if props.formattingEnum == 'NUMBER':
            # add minus before padding zeroes
            neg = '-' if line < 0 else ''
            line = abs(line)
            # int / decimal
            if not props.ifDecimal:
                line = int(line)
            
            # additional editing and segmentation
            if props.useAbbreviation:

                # get the digit count and reference the abbreviation symbol
                if line!=0:
                    digits = log(abs(line))/log(10)
                    ind = int(digits/3)
                else:
                    ind=0

                if ind<len(abbreviations) and ind>0:
                    out = formatPaddingCommas(line/10**(ind*3))
                    if props.useAbbreviationLower == True:
                        out = out+abbreviations[ind].lower()
                    else:
                        out = out+abbreviations[ind]
                else:
                    # too big for abbreviations listed or none needed
                    out = formatPaddingCommas(line)

            else:
                out = formatPaddingCommas(line)
            

        elif props.formattingEnum == 'TIME':
            out = formatCounter(line, props.timeSeparators, props.timeLeadZeroes, props.timeTrailZeroes, props.timeModulo)

    #prefix/sufix  
    if props.ifTextFile:
        text.data.body = out
        if props.ifTextFormatting and isNumeric:
            text.data.body = props.prefix + neg + out + props.sufix
    else:
        text.data.body = props.prefix + neg + out + props.sufix 

@persistent  
def textcounter_text_update_frame(scene):
    for text in scene.objects:
        if text.type == 'FONT' and text.data.text_counter_props.ifAnimated:
            textcounter_update_val(text, scene)

classes = (
    TextCounter_Props,
    TEXTCOUNTER1_PT_panel,
)
def register():
    for cls in classes:
        make_annotations(cls)
        bpy.utils.register_class(cls)
    bpy.types.TextCurve.text_counter_props = PointerProperty(type = TextCounter_Props)
    bpy.app.handlers.frame_change_post.append(textcounter_text_update_frame)

def unregister():
    bpy.utils.unregister_class(TextCounter_Props)
    bpy.utils.unregister_class(TEXTCOUNTER1_PT_panel)
    bpy.app.handlers.frame_change_post.remove(textcounter_text_update_frame)

if __name__ == "__main__":
    register()
