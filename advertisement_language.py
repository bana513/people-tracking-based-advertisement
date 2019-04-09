import re

def validate(inp):
    out = re.search(r'^[^\(]*\(.*\)[^\)]*\)$', config)
    if out: return True
    if inp == 'and': return True
    if inp == 'or': return True


    raise Exception('Validation error, unknown keyword: \'{}\''.format(inp))

def getLinkage(inp):
    validate(inp)
    res = []

    brackets = 0
    slice = []
    for c in inp:
        slice.append(c)
        if c == '(':
            if brackets == 0 and len(slice) > 1: # AND, OR, ...
                res.append(''.join(slice[:-1]))
                slice = ['(']
            brackets += 1
        elif c == ')':
            if brackets == 0:
                raise Exception('Validation error at \'{}\''.format(inp))
            brackets -= 1
            if brackets == 0:
                res.append(''.join(slice))
                slice = []

    if brackets != 0:
        raise Exception('Validation error at \'{}\''.format(inp))

    return res

# config = "((asd) OR ((qwe) AND (uio))) AND (asd)"
config = "((asd) OR ((qwe) AND (uio))) AND (asd)"
config = re.sub(r' ', '', config)
config = config.lower()
print(config)

res = getLinkage(config)
print(res)

# # out = re.sub(r'^\((.*)\) AND \((.*)\)$', r'\1\n\2', config)
# # print (out)
# out = re.search(r'^\((.*)\)AND\((.*)\)$', config)
# print(out)
# if out:
#     print("AND")
# out = re.search(r'^\((.*)\)OR\((.*)\)$', config)
# print(out)
# if out:
#     print("OR")
# print(len(out.groups()))
# # print (out.group(0))
# # print (out.group(1))
# # print (out.group(2))
# # print (out.group(3))
#
# for i,g in enumerate(out.groups()):
#     print('{}.\'{}\''.format(i,g))
