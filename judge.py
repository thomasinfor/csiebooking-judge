from telnetlib import Telnet
import re, socket, subprocess, time, random, sys, os
from contextlib import contextmanager
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-t", help="wait response time", default=0.01, dest="wt", type=float)
parser.add_argument("-r", help="existing read server ports", default=None, dest="rp", nargs="+")
parser.add_argument("-w", help="existing write server ports", default=None, dest="wp", nargs="+")
parser.add_argument("-s", help="random seed", default=7122, dest="seed", type=int)
parser.add_argument("-d", help="server file directory", default='.', dest="dir")
parser.add_argument("--debug", help="debug (noisy) mode", action='store_true', dest="debug")
args = parser.parse_args()
if args.dir: os.chdir(args.dir)
out_device = None if args.debug else subprocess.DEVNULL

WT = args.wt
TIMESTAMP = 0
random.seed(args.seed)

LIST_DATA = r"""Food: \d+ booked
Concert: \d+ booked
Electronics: \d+ booked
"""
PROMPT_CMD = r"""
Please input your booking command\. \(Food, Concert, Electronics\. Positive/negative value increases/decreases the booking amount\.\):
"""
PROMPT_EXIT = r"""
\(Type Exit to leave\.\.\.\)
"""
CMD_OK = r"""Bookings for user {id} are updated, the new booking state is:
"""
def prt(x):
    print(x)
    return x
def must(a, b, c='mismatch'):
    if a == b: return
    print(f'{a} !=!=!=!= {b}')
    raise Exception(c)
def must_match(a, b, c='mismatch'):
    if re.fullmatch(a, b): return
    print(f'{a} !=!=!=!= {b}')
    raise Exception(c)
def start_server(n_r, n_w, default_port=3000):
    def in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0;
    def find_empty_port(start):
        for i in range(start, 65536):
            if not in_use(i):
                return i
    ps, pr, pw = [], [], []
    for _ in range(n_r):
        p = find_empty_port(start=default_port)
        ps.append(subprocess.Popen(['./read_server',  str(p)], stderr=out_device, stdout=out_device))
        pr.append(p)
        time.sleep(0.2)
    for _ in range(n_w):
        p = find_empty_port(start=default_port)
        ps.append(subprocess.Popen(['./write_server',  str(p)], stderr=out_device, stdout=out_device))
        pw.append(p)
        time.sleep(0.2)
    return pr, pw, ps
def STEP(f):
    global TIMESTAMP
    def ret(*a, **b):
        global TIMESTAMP
        a[0].hey()
        TIMESTAMP += 1
        return f(*a, **b)
    return ret
class Client:
    con = False
    def __init__(self, id, port, tpe, cliID):
        if isinstance(port, list):
            self.port = port[random.randint(0, len(port)-1)]
        else:
            self.port = port
        self.id = id
        self.next = self.START
        self.cliID = cliID
        self.tpe = tpe
    def hey(self):
        global TIMESTAMP
        print(f"=================== cli = {self.cliID}, id = {self.id}, step = {TIMESTAMP} type = {self.tpe} ===================")
    def read(self):
        s = self.con.read_until(b"\0", timeout=WT).decode()
        print('>> ' + s.replace('\n', '\n>> '))
        return s
    def write(self, s):
        print('<< ' + str(s).replace('\n', '\n<< '))
        self.con.write(str(s).encode())
    def writeln(self, s):
        self.write(str(s) + '\r\n')
    def ended(self):
        try:
            self.con.read_until(b"\0", timeout=0.2)
        except EOFError:
            return True
        else:
            return False
    def close(self):
        if self.con: self.con.close()
    def quit(self):
        self.con.get_socket().send(b'\xff\xf4\xff\xfd\x06')
    def __del__(self):
        self.close()
    def step(self, p=1):
        if self.next == self.START:
            p = 1
        if random.random() >= p:
            self.next = self.QUIT
        return self.next()
    @STEP
    def START(self):
        self.con = Telnet(host="localhost", port=self.port)
        must(self.read(), 'Please enter your id (to check your booking state):\n', 'START_ERROR')
        self.next = self.ENTER_ID
        return False
    @STEP
    def ENTER_ID(self):
        self.writeln(self.id)
        s = self.read()
        if re.fullmatch(LIST_DATA + PROMPT_EXIT, s):
            self.next = self.EXIT
        elif re.fullmatch(LIST_DATA + PROMPT_CMD, s):
            self.next = self.CMD
        elif s == 'Locked.\n':
            assert self.ended()
            return True
        else:
            assert False, 'ENTER_ID_ERROR'
    @STEP
    def EXIT(self):
        self.writeln('Exit')
        assert self.ended()
        return True
    @STEP
    def CMD(self):
        self.writeln('0 0 0')
        must_match(CMD_OK.format(id=self.id) + LIST_DATA, self.read(), 'CMD_ERROR')
        assert self.ended()
        return True
    @STEP
    def QUIT(self):
        print('<< Ctrl+C')
        self.quit()
        time.sleep(WT)
        return True
def clean(ps):
    for i in ps:
        i.kill()
        i.wait()