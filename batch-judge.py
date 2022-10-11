#! /bin/python3
import os
import subprocess
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--time", help="wait response time", default=0.1, type=float)
parser.add_argument("-u", help="users", default=None, nargs="+")
parser.add_argument("-t", help="tasks", default=None, nargs="+")
parser.add_argument("--mk", help="make", action='store_true')
parser.add_argument("--test", help="test all", action='store_true')
parser.add_argument("--sum", help="summary", action='store_true')
parser.add_argument("-a", help="run all", action='store_true')
args = parser.parse_args()

TIME_LIMIT = args.time

isdir = os.path.isdir
exists = os.path.exists

lst = os.listdir()
users = [i for i in lst if exists(f'{i}/Makefile')]
tasks = [i[5:-3] for i in lst if i.startswith('test-') and i.endswith('.py')]
if args.u != None: users = [i for i in users if i in args.u]
if args.t != None: tasks = [i for i in tasks if i in args.t]

def green(str_): return "\33[32m" + str_ + "\33[0m"
def cyan(str_): return "\33[36m" + str_ + "\33[0m"
def red(str_): return "\33[31m" + str_ + "\33[0m"
def gray(str_): return "\33[2m" + str_ + "\33[0m"
print(f'tasks: ', red(' '.join(tasks)))
print(f'users: ', green(' '.join(users)))
print()

def execute(cmd, **kwargs):
    print(f'EXEC: {green(cmd)}')
    subprocess.run(cmd, shell=True, **kwargs)

def make():
    for u in users:
        execute(f'make', stderr=subprocess.DEVNULL, cwd=u)
def test():
    for t in tasks:
        for u in users:
            execute(f'python3 test-{t}.py -t {TIME_LIMIT} -d {u} > submissions/{u}--{t}.out')
def summary():
    lst = os.listdir('submissions')
    lst = [i[:-4] for i in lst if i.endswith('.out') and i.find('--') != -1]
    users = sorted(list(set([i.split('--')[0] for i in lst])))
    tasks = sorted(list(set([i.split('--')[1] for i in lst])))
    for t in tasks:
        print(red(t))
        d = dict()
        for u in users:
            f = f'submissions/{u}--{t}.out'
            if exists(f):
                with open(f) as f:
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
if args.test or args.a: test()
if args.sum or args.a: summary()