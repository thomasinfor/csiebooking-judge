from judge import *
import sys

ps = []
try:
    pr, pw, ps = args.rp, args.wp, []
    if pw == None and pw == None:
        pr, pw, ps = start_server()
    print(f'ports: r={pr}, w={pw}', file=sys.stderr)

    clis = []
    for i in range(50):
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