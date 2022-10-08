from judge import *
import sys

random.seed(7122)
ps = []
try:
    WT = 0.05
    pr, pw, ps = start_server(1, 1)
    # pr, pw = 8888, 9999
    print(f'ports: r={pr}, w={pw}', file=sys.stderr)

    clis = []
    for i in range(500):
        if random.randint(0, 1):
            clis.append(Client(
                id=random.randint(902001, 902020),
                port=pr,
                tpe='RD',
                cliID=len(clis)
            ))
        else:
            clis.append(Client(
                id=random.randint(902001, 902020),
                port=pw,
                tpe='WR',
                cliID=len(clis)
            ))

    while clis:
        i = random.randint(0, len(clis)-1)
        if clis[i].step():
            clis.pop(i)
        if TIMESTAMP in []: input()
finally:
    clean(ps)