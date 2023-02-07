# remove all lines that don't have a certain substring in them in a file
# Usage: python cleantrace.py <filename> <substring>

import sys

if len(sys.argv) != 3:
    print "Usage: python cleantrace.py <filename> <substring>"
    sys.exit(1)

filename = sys.argv[1]
substring = sys.argv[2]

f = open(filename, 'r')
lines = f.readlines()
for line in lines:
    if substring not in line:
        lines.remove(line)
f.close()

f = open(filename, 'w')
f.writelines(lines)
f.close()
