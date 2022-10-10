#! /bin/python3
import os, subprocess, re
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--time", help="wait response time", default=0.1, type=float)
parser.add_argument("-t", help="specify tasks", default=None, nargs="+")
parser.add_argument("--name", help="username ([a-zA-Z0-9_]+), make it short", required=True)
parser.add_argument("--mk", help="make", action='store_true')
parser.add_argument("--run", help="run all tasks", action='store_true')
parser.add_argument("--sum", help="summary", action='store_true')
parser.add_argument("--submit", help="submit mode", action='store_true')
parser.add_argument("-a", help="--run + --sum + --submit", action='store_true')
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
        for i in rk:
            c = green if len(i) == len(rk[0]) else gray
            print(c('\t'.join([str(len(i))] + i)))

if args.mk or args.a: make()
if args.run or args.a: test()
if args.sum or args.a: summary()