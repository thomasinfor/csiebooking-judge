#! /bin/python3
import os, subprocess, re
from argparse import ArgumentParser
from utils import split, squeeze

parser = ArgumentParser()
parser.add_argument("--time", default=0.1, type=float, help="wait response time (default 0.1)")
parser.add_argument("-t", default=None, nargs="+", help="specify tasks")
parser.add_argument("--name", required=True, help="username ([a-zA-Z0-9_]+), make it short")
parser.add_argument("--mk", action='store_true', help="make")
parser.add_argument("--run", action='store_true', help="run all tasks")
parser.add_argument("--sum", action='store_true', help="summary")
parser.add_argument("--teacher", default=False, nargs='?', const=None, help="compare your output with whose? (leave blank for auto detection)")
parser.add_argument("-a", action='store_true', help="--mk + --run + --sum")
args = parser.parse_args()

TIME_LIMIT = args.time

isdir = os.path.isdir
exists = os.path.exists
def rel_here(*p): return os.path.join(os.path.dirname(os.path.abspath(__file__)), *p)
def rel_cwd(*p): return os.path.join(os.getcwd(), *p)

user = args.name
assert re.fullmatch(r'[a-zA-Z0-9_]+', user)
tasks = [i[5:-3] for i in os.listdir(rel_here()) if i.startswith('test-') and i.endswith('.py')]
if args.t != None: tasks = [i for i in tasks if i in args.t]

def green(str_): return "\33[32m" + str_ + "\33[0m"
def cyan(str_): return "\33[36m" + str_ + "\33[0m"
def red(str_): return "\33[31m" + str_ + "\33[0m"
def gray(str_): return "\33[2m" + str_ + "\33[0m"
print(f'tasks: ', red(' '.join(tasks)))
print(f'user: ', green(user))
print()

def execute(cmd, **kwargs):
    if isinstance(cmd, list):
        print(f'EXEC: {green(" ".join(cmd))}')
    else:
        print(f'EXEC: {green(cmd)}')
    subprocess.run(cmd, shell=False, **kwargs)

def make():
    execute(f'make', stderr=subprocess.DEVNULL, cwd=rel_cwd())
def test():
    for t in tasks:
        with open(rel_here(f'submissions/{user}--{t}.out'), 'w+') as f:
            execute(['python3', rel_here(f'test-{t}.py'), '-t', f'{TIME_LIMIT}'], stdout=f)
leader = dict()
def summary():
    lst = os.listdir(rel_here('submissions'))
    lst = [i[:-4] for i in lst if i.endswith('.out') and i.find('--') != -1]
    users = sorted(list(set([i.split('--')[0] for i in lst])))
    tasks = sorted(list(set([i.split('--')[1] for i in lst])))
    # print(users, tasks)
    for t in tasks:
        print(red(t))
        d = dict()
        for u in users:
            f = f'submissions/{u}--{t}.out'
            if exists(rel_here(f)):
                with open(rel_here(f), 'r') as f:
                    s = f.read()
                if s in d:
                    d[s].append(u)
                else:
                    d[s] = [u]
        rk = sorted(list(d.values()), key=lambda x: -len(x))
        if rk: leader[t] = rk[0][0]
        for i in rk:
            c = green if len(i) == len(rk[0]) else gray
            print(c('\t'.join([str(len(i))] + i)))
def teach():
    for t in tasks:
        fa = f'submissions/{user}--{t}.out'
        if not exists(rel_here(fa)): continue
        teacher = args.teacher if args.teacher != None else leader[t]
        fb = f'submissions/{teacher}--{t}.out'
        if not exists(rel_here(fb)): continue
        with open(rel_here(fb), 'r') as f:
            T = f.read()
        with open(rel_here(fa), 'r') as f:
            U = f.read()
        if T == U: continue
        print(f'{red(t)}:\t{green(teacher)} vs {gray(user)}')
        T = split(T)
        U = split(U)
        n = min(len(T), len(U))
        if T[:n] == U[:n]:
            pass
        else:
            for i in range(n):
                if T[i] != U[i]:
                    break
            U = [x for x in U[:i+1] if x[0] == U[i][0]]
            print(cyan(f'Difference found at step {i} (id = {T[i][0]})'))
            print(gray(squeeze(U)), end='')
            print(green(T[i][1][T[i][1].find('\n')+1:]))

if args.mk or args.a: make()
if args.run or args.a: test()
if args.teacher != False or args.sum or args.a: summary()
if args.teacher != False or args.a: teach()