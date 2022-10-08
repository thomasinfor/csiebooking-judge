import sys, re

sep = r'=+ .+id = (\d+).+ =+'
def split(s):
    res = list(re.finditer(sep, s))
    steps = []
    for i in range(len(res)):
        if i == len(res)-1:
            steps.append(s[res[i].start():len(s)])
        else:
            steps.append(s[res[i].start():res[i+1].start()])
        steps[-1] = [res[i].group(1), steps[-1]]
    return steps
def squeeze(x): return ''.join([i[1] for i in x])