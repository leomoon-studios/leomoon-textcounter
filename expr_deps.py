import re

inclusion = ".evaluated_get(dp)"
regex_parts = (
    r'\.active_object\W',
    r'\.object\W',
    r'\.objects[\[\(]',
    r'\.objects\.get\W',
    
    r'scene\W',
    r'\.scenes[\[\(]',
    r'\.scenes\.get\W',
    
    r'\.material\W',
    r'\.materials[\[\(]',
    r'\.materials\.get\W',
    
    r'\.data\.\w+?\W',
    r'\.data\.\w+?\.get\W',
    
    r'\.data\W',
    r'\.data\.get\W',

    r'\.parent\W',
)

regex = '|'.join(regex_parts)

def eval_parser(expression, begin=0, end=-1):
    offset = 0
    read_till = None
    read_till_string = None
    parenthesis_count = 0
    while m := re.search(regex, expression[offset:]):
        i = offset + m.end() -1
        if expression[i] == '.':
            expression = expression[:i] + inclusion + expression[i:]
            offset += m.end() + len(inclusion)-1
            continue
        
        caret = i-1
        for i, c in enumerate(expression[caret:]):
            if read_till_string is not None:
                if c == read_till_string:
                    read_till_string = None
                continue
            elif read_till is not None:
                if c == read_till and parenthesis_count == 1:
                    read_till = None
                    parenthesis_count = 0
                    break
            
            if c in {"'", '"'}:
                read_till_string = c
            elif c == '[':
                if not read_till:
                    read_till = ']'
                if read_till == ']':
                    parenthesis_count += 1
            elif c == ']':
                if read_till == ']':
                    parenthesis_count -= 1
            
            elif c == '(':
                if not read_till:
                    read_till = ')'
                if read_till == ')':
                    parenthesis_count += 1
            elif c == ')':
                if read_till == ')':
                    parenthesis_count -= 1

        i = caret + i
        expression = expression[0:i+1] + inclusion + expression[i+1:]
        offset += caret  + len(inclusion)-1
    return expression


def _sanitize(s):
    return s.replace('__', '').replace('ops', '_').replace('preferences', '_').replace('utils', '_').replace('new', '_').replace('load', '_')

def sanitize_str(s):
    regex = r'[\'\"]'

    indexes = []
    qtype = None
    for m in re.finditer(regex, s):
        if qtype is None:
            qtype = m.group()
            indexes.append(m.start())
        elif qtype == m.group():
            qtype = None
            indexes.append(m.start())

    start_idx = 0
    new_str = ""
    is_str = False
    while indexes:
        i = indexes.pop(0)
        new_str += _sanitize(s[start_idx: i] if is_str else s[start_idx: i])
        start_idx = i
        is_str = not is_str
    new_str += _sanitize(s[start_idx:] if is_str else s[start_idx:])

    return new_str

if __name__ == '__main__':
    def passert(a, b):
        try:
            assert a == b
        except:
            print('Assert Error')
            print('A:', a)
            print('B:', b)

    passert( eval_parser("scene.objects[foo.bar['Alice ] Bob'].bar[23]].location.x"), "scene.evaluated_get(dp).objects[foo.bar['Alice ] Bob'].bar[23]].evaluated_get(dp).location.x" )
    passert( eval_parser("scene.objects['Cube'].location.x"), "scene.evaluated_get(dp).objects['Cube'].evaluated_get(dp).location.x" )
    passert( eval_parser("scene.objects.get('Cube 1').location.x + 3.156"), "scene.evaluated_get(dp).objects.get('Cube 1').evaluated_get(dp).location.x + 3.156" )
    passert( eval_parser("scene.objects['Cube ' + str(int(int(1.real).real.real))].location.x + 3.15"), "scene.evaluated_get(dp).objects['Cube ' + str(int(int(1.real).real.real))].evaluated_get(dp).location.x + 3.15" )
    passert( eval_parser("scene.objects['Cube '+str(1)].location.x + 3.145"), "scene.evaluated_get(dp).objects['Cube '+str(1)].evaluated_get(dp).location.x + 3.145" )
    passert( eval_parser("scene.objects[0]"), "scene.evaluated_get(dp).objects[0].evaluated_get(dp)" )
    passert( eval_parser("scene.objects.get('Cube ' + str(1))"), "scene.evaluated_get(dp).objects.get('Cube ' + str(1)).evaluated_get(dp)" )
    passert( eval_parser("scene.objects['Cube 1'].location.x + 3.9"), "scene.evaluated_get(dp).objects['Cube 1'].evaluated_get(dp).location.x + 3.9" )
    passert( eval_parser('C.scene.objects["Cube 1"].material_slots[0].material.refraction_depth'), 'C.scene.evaluated_get(dp).objects["Cube 1"].evaluated_get(dp).material_slots[0].material.evaluated_get(dp).refraction_depth' )
    
    passert( sanitize_str("__D.objects.preferences.__class__[\'__Light__\"__'].bpy.ops.do_some().__"), '''D.objects._.class['__Light__"__'].bpy._.do_some().''' )