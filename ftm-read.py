import os
import mmap
import serial
import struct

s = serial.Serial("/dev/radio/digirig0", baudrate=38400, rtscts=False)
s.timeout = 5

chunk = -1
addrs = []

image_size = 0x18000 + (128 * 2)
with open('radio.img', 'wb') as fd:
    fd.write(b'\x00' * image_size)

with open('radio.img', 'r+b') as fd:
    image = mmap.mmap(fd.fileno(), 0, flags=mmap.MAP_SHARED)

    while True:
        frame = s.read(131)
        if not len(frame):
            break

        (addr,) = struct.unpack(">H", frame[0:2])
        if addr == 0:
            chunk += 1
            base = chunk * 0x10000

        if addr in [0xfffd, 0xfffe]:
            pos = 2 if addr == 0xfffd else 1
            addr = image_size - (pos * 128)
        else:
            addr += base

        print(f"addr {addr:06x}")

        block = frame[2:130]
        have_checksum = frame[130]
        want_checksum = sum(frame[:-1]) % 256

        if have_checksum != want_checksum:
            raise ValueError(
                f"ERROR: invalid checksum @ {addr}, want {want_checksum}, have {have_checksum}"
            )

        image[addr : addr + 128] = block
        s.write(b"\x06")
