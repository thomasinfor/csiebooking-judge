from judge import *
import sys

ps = []
try:
    pr, pw, ps = args.rp, args.wp, []
    if pr == None and pw == None:
        pr, pw, ps = start_server(1, 1)
    print(f'ports: r={pr}, w={pw}', file=sys.stderr)
    init_record()

    ###############################################################
    # test if A's lock is affected when B unlocks
    A = Client(id=902001, port=pr, tpe='RD', cliID='R01')
    B = Client(id=902002, port=pr, tpe='RD', cliID='R02')
    C = Client(id=902001, port=pw, tpe='WR', cliID='W01')

    A.START()
    B.START()
    C.START()

    A.ENTER_ID()
    B.ENTER_ID()
    B.EXIT()

    C.ENTER_ID()
    # C should be locked, since A haven't exited
    C.QUIT()
    A.QUIT()
    ###############################################################
finally:
    clean(ps)