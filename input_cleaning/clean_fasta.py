import sys

infile = sys.argv[1]
outfile = sys.argv[2]

out = open(outfile, 'w')

count = 0

for line in open(infile):
    if len(line) == 0 or line[0] == '>':
        out.write(line)
    else:
        chars = []
        for c in line.strip():
            if c in ['a', 'c', 'g', 't', 'A', 'C', 'G', 'T']:
                chars.append(c.upper())
            else:
                chars.append('A')
                count += 1
        out.write("".join(chars) + "\n")

print("Replaced ", count, " characters")

