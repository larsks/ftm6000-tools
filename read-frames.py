import base64
import struct
import hexdump
import json
import sys

with open(sys.argv[1]) as fd:
    frames = json.load(fd)

chunk = -1
last_addr = 0

for frame in frames:
    data = base64.b64decode(frame["frame"])
    addr, = struct.unpack('>H', data[0:2])
    block = data[2:130]
    checksum = data[130]

    if addr == 0:
        chunk += 1
        base = chunk * 0x10000

    adj_addr = base + addr
    print(f'@ {addr:04x} ({adj_addr:04x})')

    if adj_addr != last_addr + 128:
        print(f'Gap! {last_addr:04x} -> {adj_addr:04x}')

    hexdump.hexdump(block)

    last_addr = adj_addr
