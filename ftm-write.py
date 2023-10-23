import hexdump
import serial
import mmap
import struct

image_size = 0x18000 + (128 * 2)

ranges = [
    (0x0, 0x0),
    (0x100, 0x380),
    (0x480, 0x17F80),
    (0xFFFD, 0xFFFD),
    (0xFFFE, 0xFFFE),
]

s = serial.Serial("/dev/radio/digirig0", baudrate=38400, rtscts=False)
s.timeout = 5

with open("radio.img", "rb") as fd:
    image = mmap.mmap(fd.fileno(), 0, flags=mmap.MAP_PRIVATE)

    for low, high in ranges:
        for addr in range(low, high + 1, 128):
            print(hex(addr))

            if addr in [0xFFFD, 0xFFFE]:
                target_addr = addr
                pos = 2 if addr == 0xFFFD else 1
                addr = image_size - (pos * 128)
            else:
                target_addr = addr & 0xFFFF

            frame = bytearray(131)
            frame[0:2] = struct.pack(">H", target_addr)
            frame[2:130] = image[addr : addr + 128]
            checksum = sum(frame[:130]) % 256
            frame[130] = checksum

            hexdump.hexdump(frame)

            s.write(frame)
            res = s.read(1)
            if res != b"\x06":
                raise ValueError(f"unexpected response from radio: {res}")
