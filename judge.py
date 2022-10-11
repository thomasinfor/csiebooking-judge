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

INIT_RECORD = b'q\xc3\r\x00\x03\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00r\xc3\r\x00\x02\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00s\xc3\r\x00\x02\x00\x00\x00\x04\x00\x00\x00\x04\x00\x00\x00t\xc3\r\x00\x04\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00u\xc3\r\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00v\xc3\r\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00w\xc3\r\x00\x00\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00x\xc3\r\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00y\xc3\r\x00\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00z\xc3\r\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00{\xc3\r\x00\x02\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00|\xc3\r\x00\x03\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00}\xc3\r\x00\x01\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00~\xc3\r\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x7f\xc3\r\x00\x03\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x80\xc3\r\x00\x01\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x81\xc3\r\x00\x04\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x82\xc3\r\x00\x01\x00\x00\x00\x04\x00\x00\x00\x04\x00\x00\x00\x83\xc3\r\x00\x01\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x84\xc3\r\x00\x03\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00'
LIST_DATA = r"""Food: (\d+) booked
Concert: (\d+) booked
Electronics: (\d+) booked
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
        default_port = p+1
        time.sleep(0.2)
    for _ in range(n_w):
        p = find_empty_port(start=default_port)
        ps.append(subprocess.Popen(['./write_server',  str(p)], stderr=out_device, stdout=out_device))
        pw.append(p)
        default_port = p+1
        time.sleep(0.2)
    return pr, pw, ps
def init_record(rec=INIT_RECORD):
    with open('./bookingRecord', 'wb+') as f:
        f.write(rec)
def gen_invalid_num():
    a = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-0123456789"
    return ''.join([random.choice(list(a)) for _ in range(random.randint(1, 5))])
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
    cmd_p = 1
    def __init__(self, id, port, tpe, cliID):
        if isinstance(port, list):
            self.port = random.choice(port)
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
    def fullmatch(self, *a, **b):
        self.match = re.fullmatch(*a, **b)
        return self.match
    def valid(self, c):
        if len(c.split(' ')) != 3: return False
        try:
            c = [int(i) for i in c.split(' ')]
            cnt = 0
            for i in range(3):
                if c[i] + self.dat[i] < 0:
                    return False
                cnt += c[i] + self.dat[i]
            return cnt <= 15
        except:
            return False
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
        if self.fullmatch(LIST_DATA + PROMPT_EXIT, s):
            self.next = self.EXIT
        elif self.fullmatch(LIST_DATA + PROMPT_CMD, s):
            self.dat = [int(self.match[1]), int(self.match[2]), int(self.match[3])]
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
        if self.cmd_p == 1:
            self.writeln('0 0 0')
        else:
            if random.random() <= self.cmd_p:
                while True:
                    x = f'{random.randint(-3, 3)} {random.randint(-3, 3)} {random.randint(-3, 3)}'
                    if not self.valid(x): continue
                    self.writeln(x)
                    break
            else:
                while True:
                    x = f'{gen_invalid_num()} {gen_invalid_num()} {gen_invalid_num()}'
                    if self.valid(x): continue
                    self.writeln(x)
                    break
        rd = self.read()
        if self.cmd_p == 1:
            assert self.fullmatch(CMD_OK.format(id=self.id) + LIST_DATA, rd), 'CMD_ERROR'
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