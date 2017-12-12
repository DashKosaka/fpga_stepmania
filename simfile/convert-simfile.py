import struct

with open('starbow.sm','r') as inf:
    notelist = inf.readlines()
    notelist = [ x.strip() for x in notelist ]
    notelist = [ int(x,2) for x in notelist ]  # binary
    outfile = open('simfile.rom','wb')
    for x in notelist:
        outfile.write(struct.pack("h",x))
