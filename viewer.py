import sys, re
from utils import split, squeeze

file, ID, *_ = sys.argv[1:]

print(f'Extracting operations about {ID} in file {file}')

sep = r'=+ .+id = (\d+).+ =+'

with open(file, 'r') as f:
    s = f.read()
    steps = [i for i in split(s) if i[0] == ID]
    print(squeeze(steps))