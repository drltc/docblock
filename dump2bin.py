#!/usr/bin/env python3

import codecs
import sys

with open("socket.out", "r") as f:
    while True:
        control = f.readline()
        if control == "":
            break
        sys.stderr.write(control)
        data = f.readline()
        if control.startswith(">"):
            continue
        data = data.strip()
        data = data.replace(" ", "")
        cdata = codecs.decode(data, "hex_codec")
        sys.stdout.buffer.write(cdata)

sys.stdout.close()

