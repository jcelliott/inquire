""" clean TREC data files """

import fileinput
import sys
import re
from bs4 import BeautifulSoup

FILE = 'trec_2003.txt'
OUTFILE = 'trec_2003_cleaned.txt'

data = ""

for line in fileinput.input(FILE):
    if line.startswith('<num>'):
        data += re.sub(r'<num> Number: (\d+).*', r'<num>\1</num>', line)
    elif line.startswith('<type>'):
        data += re.sub(r'<type> Type: (\w+).*', r'<type>\1</type>', line)
    elif line.startswith('<desc>'):
        data += '<desc>'
    elif line.startswith('</top>'):
        data += '</desc></top>'
    else:
        data += line


soup = BeautifulSoup(data, 'lxml')
questions = []
tops = soup.find_all('top')

for t in tops:
    num = t.find('num').string
    typ = t.find('type').string
    q = t.find('desc').string.strip()
    questions.append((num, typ, q))

with open(OUTFILE, 'w') as out:
    for q_line in questions:
        # print(q_line)
        out.write("{0} {1} {2}\n".format(*q_line))
