""" tokenize data to match existing dataset """
from __future__ import absolute_import, division, print_function
import fileinput
import re

FILE = 'trec_2002_final.txt'

for line in fileinput.input(FILE):
    # order is important
    line = re.sub(r'([.!?])$', r' \1', line)
    line = re.sub(r'(\w+)([.!?])', r'\1 \2', line)
    line = re.sub(r"'(.*)'", r"` \1 '", line)
    line = re.sub(r'"(.*)"', r"`` \1 ''", line)
    line = re.sub(r"(\w+)'s", r"\1 's", line)
    line = re.sub(r"(\w+)'", r"\1 '", line)
    line = re.sub(r'(\w+)([,:;-]) ', r'\1 \2 ', line)
    print(line.strip())
