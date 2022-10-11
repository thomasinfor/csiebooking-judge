#! /bin/python3
import sys, re
from utils import split, squeeze

fa, fb, *_ = sys.argv[1:]

print(f'Finding first difference between file {fa} and file {fb}')

sep = r'=+ .+id = (\d+).+ =+'

with open(fa, 'r') as f:
    a = f.read()
    a = split(a)
with open(fb, 'r') as f:
    b = f.read()
    b = split(b)

if a == b:
    print('identical!!')
else:
    n = min(len(a), len(b))
    if a[:n] == b[:n]:
        a.append(['', ''])
        b.append(['', ''])
        print(f'>>>>>>> {fa}')
        print(a[n][1])
        print('-------')
        print(b[n][1])
        print(f'<<<<<<< {fb}')
    else:
        for i in range(n):
            if a[i] != b[i]:
                print(f'>>>>>>> {fa}')
                print(a[i][1])
                print('-------')
                print(b[i][1])
                print(f'<<<<<<< {fb}')
                break