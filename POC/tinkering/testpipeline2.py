#! /usr/bin/env python3
import subprocess
import sys
import os
import zlib
# First command: 'ls -l'
p1 = subprocess.Popen(['ls', '-l', '../cloudadmin'], stdout=subprocess.PIPE)

# second command is 'cat'
p2 = subprocess.Popen(['cat'],stdin=subprocess.PIPE,stdout=sys.stdout)

# Fast compressor object
compressor=zlib.compressobj(level=1,wbits=27)

# This loop is supposed to run the first command, read its output in 1KB chunks, compress each chunk,
# then send as the input of second command
# Test is effectively:   ls -l | gzip -c | cat
# This is to mock what we eventually  want
#       rclone lsjson | gzip -c | rclone rcat

chunk_size=1024
while True:
    # read a chunk_size of output
    chunk = p1.stdout.read(chunk_size)
    if not chunk:
        break
    # compress it
    zoutput=compressor.compress(chunk)
    # write to the second process
    p2.stdin.write(zoutput)


# get the last of the compressed output and write it to the second process
zoutput=compressor.flush(zlib.Z_FINISH)
p2.stdin.write(zoutput)
# close the stdin of p2 to let it know we are done with it.
p2.stdin.close()
# Wait until p2 is done
p2.wait()
